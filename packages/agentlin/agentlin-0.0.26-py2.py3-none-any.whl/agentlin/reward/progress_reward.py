import argparse
from collections import defaultdict
import copy
from dataclasses import dataclass
import json
import math
from pathlib import Path
import pdb
from typing import Literal
import pandas as pd

import util
from vllm import LLM, SamplingParams
import sys
import torch
import numpy as np
from tqdm import tqdm
from itertools import accumulate

from loguru import logger
from xlin import load_json_or_jsonl, save_df_dict, datetime_str

from transformers import AutoModelForSequenceClassification, AutoModel, AutoTokenizer, AutoModelForCausalLM, PreTrainedModel, PreTrainedTokenizer

def batched_math_shepherd_inference(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    inputs: list[str],
    batch_size: int,
    STEP_TAG_ID: int,
    CANDIDATE_TOKENS: list[int],
) -> list[list[float]]:
    # for i in range(len(inputs)):
    #     print()
    #     print(f"{i}".center(30, "="))
    #     print(inputs[i])
    #     print()
    output_scores = []
    for i in tqdm(range(0, len(inputs), batch_size), desc="Process reward computation"):
        inputs_batch = inputs[i : i + batch_size]
        inputs_batch = tokenizer(inputs_batch, padding=True, return_tensors="pt")
        inputs_batch = inputs_batch.to(model.device)
        with torch.no_grad():
            logits = model(**inputs_batch).logits[:, :, CANDIDATE_TOKENS]
            scores = logits.softmax(dim=-1)[:, :, 0]
            step_scores_flat = scores[inputs_batch.input_ids == STEP_TAG_ID].tolist()
            # Split scores into sublist based on number of \n in the input
            step_scores = []
            counter = 0
            for i in range(len(inputs_batch.input_ids)):
                count = inputs_batch.input_ids[i].tolist().count(STEP_TAG_ID)
                step_scores.append(step_scores_flat[counter : counter + count])
                counter += count

        # Store the step scores for this batch
        output_scores.extend(step_scores)

        # Clear GPU memory
        del inputs_batch, logits, scores
        torch.cuda.empty_cache()

    return output_scores


class PRM:
    def __init__(self, args, **model_kwargs):
        self.args = args
        self.placeholder_token = self.args.placeholder_token # "ки"
        self.reward_tokens = self.args.reward_tokens # ["+", "-"]
        self.placeholder_token_in_tokenizer = self.args.placeholder_token_in_tokenizer # "<|reserved_special_token_0|>"
        self.reward_tokens_in_tokenizer = self.args.reward_tokens_in_tokenizer # self.reward_tokens
        self.model, self.tokenizer = self.load_model_and_tokenizer(**model_kwargs)

    def load_model_and_tokenizer(self, **model_kwargs) -> tuple[PreTrainedModel, PreTrainedTokenizer]:
        raise NotImplementedError

    def score(self, questions: list[str], outputs: list[list[str]]) -> list[list[list[float]]]:
        raise NotImplementedError


class RandomReward(PRM):
    def load_model_and_tokenizer(self) -> tuple[PreTrainedModel, PreTrainedTokenizer]:
        tokenizer = None
        model = None
        return model, tokenizer

    def score(self, questions: list[str], outputs: list[list[str]]) -> list[list[float]]:
        output_scores = []
        for question, output in zip(questions, outputs):
            output_score = [[np.random.rand() for _ in range(100)] for o in output]
            output_scores.append(output_score)

        # stripped_output_scores = [] TODO: strip out the reward for previous steps
        for output_score, output in zip(output_scores, outputs):
            assert len(output_score) == len(output), f"{len(output_score)} != {len(output)}"

        return output_scores

class MathShepherd(PRM):
    def load_model_and_tokenizer(self) -> tuple[PreTrainedModel, PreTrainedTokenizer]:
        model_id = "peiyi9979/math-shepherd-mistral-7b-prm"
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        # For batched inference
        tokenizer.pad_token = tokenizer.eos_token
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map=self.args.prm_device,
            attn_implementation="flash_attention_2",
            torch_dtype=torch.float16,
        ).eval()
        return model, tokenizer

    def score(self, questions: list[str], outputs: list[list[str]]) -> list[list[float]]:
        system_prompt: str = "Solve the following math problem efficiently and clearly:\n\n- For simple problems (2 steps or fewer):\nProvide a concise solution with minimal explanation.\n\n- For complex problems (3 steps or more):\nUse this step-by-step format:\n\n## Step 1: [Concise description]\n[Brief explanation and calculations]\n\n## Step 2: [Concise description]\n[Brief explanation and calculations]\n\n...\n\nRegardless of the approach, always conclude with:\n\nTherefore, the final answer is: $\\boxed{answer}$. I hope it is correct.\n\nWhere [answer] is just the final number or expression that solves the problem."
        CANDIDATE_TOKENS = [648, 387]
        STEP_TAG_ID = 12902
        inputs_for_prm = []
        lengths = []
        for question, output in zip(questions, outputs):
            prompt = system_prompt + "\n" + question + "\n"
            special_outputs = [o.replace("\n\n", " ки\n\n") for o in output]
            special_outputs = [
                o + " ки" if o[-2:] != "\n\n" else o for o in special_outputs
            ]
            inputs_for_prm.extend([f"{prompt} {o}" for o in special_outputs])
            lengths.append(len(output))

        # TODO: tokenize each batch independently so there is less padding and faster inference
        output_scores = batched_math_shepherd_inference(
            self.model,
            self.tokenizer,
            inputs_for_prm,
            self.args.prm_batch_size,
            STEP_TAG_ID,
            CANDIDATE_TOKENS,
        )
        cumulative_lengths = list(accumulate(lengths))
        # reshape the output scores to match the input
        output_scores = [
            output_scores[i:j]
            for i, j in zip([0] + cumulative_lengths[:-1], cumulative_lengths)
        ]

        # stripped_output_scores = [] TODO: strip out the reward for previous steps
        for output_score, output in zip(output_scores, outputs):
            assert len(output_score) == len(output), f"{len(output_score)} != {len(output)}"

        return output_scores


class RLHFFlow(PRM):
    def load_model_and_tokenizer(self, **model_kwargs) -> tuple[PreTrainedModel, PreTrainedTokenizer]:
        model_path = "RLHFlow/Llama3.1-8B-PRM-Deepseek-Data"
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            device_map=self.args.prm_device,
            torch_dtype=torch.bfloat16,
            **model_kwargs,
        ).eval()
        tokenizer.padding_side = "right"
        tokenizer.pad_token = tokenizer.eos_token
        model.config.pad_token_id = model.config.eos_token_id

        plus_tag_id = tokenizer.encode("+")[-1]
        minus_tag_id = tokenizer.encode("-")[-1]
        self.candidate_tokens = [plus_tag_id, minus_tag_id]

        return model, tokenizer

    def score(
        self,
        questions: list[str],
        outputs: list[list[str]],
        batched: bool = True,
        batch_size=8,
    ) -> list[list[float]]:
        if batched is True:
            return self._score_batched(questions, outputs, batch_size=batch_size)
        else:
            return self._score_single(questions, outputs)

    def _score_single(self, questions: list[str], outputs: list[list[str]]):
        # reference code: https://github.com/RLHFlow/RLHF-Reward-Modeling/blob/main/math-rm/prm_evaluate.py
        all_scores = []
        for question, answers in zip(questions, outputs, strict=True):
            all_step_scores = []
            for ans in answers:
                single_step_score = []
                conversation = []
                ans_list = ans.split("\n\n")
                for k in range(len(ans_list)):
                    if k == 0:
                        # TODO: add the system prompt like we did for math shepard?
                        text = question + " " + ans_list[0]
                    else:
                        text = ans_list[k]
                    conversation.append({"content": text, "role": "user"})
                    conversation.append({"content": "+", "role": "assistant"})
                    input_ids = self.tokenizer.apply_chat_template(
                        conversation, return_tensors="pt"
                    ).to(self.model.device)
                    with torch.no_grad():
                        logits = self.model(input_ids).logits[
                            :, -3, self.candidate_tokens
                        ]  # simple version, the +/- is predicted by the '-3' position
                        step_scores = logits.softmax(dim=-1)[
                            :, 0
                        ]  # 0 means the prob of + (1 mean -)
                        # print(scores)
                        single_step_score.append(
                            step_scores[0]
                            .detach()
                            .to("cpu", dtype=torch.float32)
                            .item()
                        )

                all_step_scores.append(single_step_score)
            all_scores.append(all_step_scores)
        return all_scores

    def _score_batched(self, questions: list[str], outputs: list[list[str]], batch_size: int = 2):
        # The RLHFlow models are trained to predict the "+" or "-" tokens in a dialogue, but since these are not unique
        # we need to introduce a dummy special token here for masking.

        special_tok_id = self.tokenizer("ки", return_tensors="pt").input_ids[0, 1]
        # We construct two parallel dialogues, one with a "+" token per assistant turn, the other with the dummy token "ки" for masking
        conversations = []
        conversations2 = []
        for question, answers in zip(questions, outputs, strict=True):
            for ans in answers:
                conversation = []
                conversation2 = []
                ans_list = ans.split("ки\n")
                for k in range(len(ans_list)):
                    if k == 0:
                        text = question + " " + ans_list[0]
                    else:
                        text = ans_list[k]
                    conversation.append({"content": text.strip("ки").strip(), "role": "user"})
                    conversation.append({"content": "+", "role": "assistant"})

                    # we track to location of the special token with ки in order to extract the scores
                    conversation2.append({"content": text, "role": "user"})
                    conversation2.append({"content": "ки", "role": "assistant"})

                conversations.append(conversation)
                conversations2.append(conversation2)

        output_scores = []
        for i in range(0, len(conversations), batch_size):
            convs_batch = conversations[i : i + batch_size]
            convs2_batch = conversations2[i : i + batch_size]
            inputs_batch = self.tokenizer.apply_chat_template(
                convs_batch, padding=True, return_tensors="pt"
            ).to(self.model.device)
            inputs2_batch = self.tokenizer.apply_chat_template(
                convs2_batch, padding=True, return_tensors="pt"
            ).to(self.model.device)
            assert inputs_batch.shape == inputs2_batch.shape
            with torch.no_grad():
                logits = self.model(inputs_batch).logits[:, :, self.candidate_tokens]
                scores = logits.softmax(dim=-1)[:, :, 0]  # 0 means the prob of + (1 mean -)

                for i in range(len(convs_batch)):
                    # We slice on the N-1 token since the model is trained to predict the Nth one ("+" in this case)
                    step_scores_flat = scores[i, :-1][inputs2_batch[i, 1:] == special_tok_id].tolist()
                    output_scores.append(step_scores_flat)

        # reshape the output scores to match the input
        reshaped_output_scores = []
        counter = 0
        for question, answers in zip(questions, outputs):
            scores = []
            for answer in answers:
                scores.append(output_scores[counter])
                counter += 1
            reshaped_output_scores.append(scores)

        return reshaped_output_scores


class QwenPRM(PRM):
    def load_model_and_tokenizer(self) -> tuple[PreTrainedModel, PreTrainedTokenizer]:
        model_id = "Qwen/Qwen2.5-Math-PRM-7B"
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        # For batched inference
        tokenizer.pad_token = tokenizer.eos_token
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map=self.args.prm_device,
            attn_implementation="flash_attention_2",
            torch_dtype=torch.float16,
        ).eval()
        tokenizer.add_special_tokens({"additional_special_tokens": [self.placeholder_token_in_tokenizer] + self.reward_tokens_in_tokenizer})
        logger.info(f"Placeholder token: {self.placeholder_token_in_tokenizer} and reward tokens: {self.reward_tokens_in_tokenizer} added to tokenizer as special tokens")

        self.STEP_TAG_ID = tokenizer.encode(self.placeholder_token_in_tokenizer, add_special_tokens=False)[0]
        self.CANDIDATE_TOKENS = tokenizer.encode(["+", "-"], add_special_tokens=False)
        return model, tokenizer

    def score(self, questions: list[str], outputs: list[list[str]]) -> list[list[float]]:
        system_prompt: str = "Please reason step by step, and put your final answer within \boxed{}."

        placeholder_token = self.placeholder_token
        placeholder_token_in_tokenizer = self.placeholder_token_in_tokenizer
        inputs_for_prm = []
        lengths = []
        for question, output in zip(questions, outputs):
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ]
            for o in output:
                o = o.replace(placeholder_token, placeholder_token_in_tokenizer).rstrip()
                if not o.endswith(placeholder_token_in_tokenizer):
                    o = o + placeholder_token_in_tokenizer
                prompt = self.tokenizer.apply_chat_template(
                    messages + [{"role": "assistant", "content": o}],
                    tokenize=False,
                    add_generation_prompt=False
                )
                inputs_for_prm.append(prompt)
            lengths.append(len(output))

        # TODO: tokenize each batch independently so there is less padding and faster inference
        output_scores = batched_math_shepherd_inference(
            self.model,
            self.tokenizer,
            inputs_for_prm,
            self.args.prm_batch_size,
            self.STEP_TAG_ID,
            self.CANDIDATE_TOKENS,
        )
        cumulative_lengths = list(accumulate(lengths))
        # reshape the output scores to match the input
        output_scores = [
            output_scores[i:j]
            for i, j in zip([0] + cumulative_lengths[:-1], cumulative_lengths)
        ]

        # stripped_output_scores = [] TODO: strip out the reward for previous steps
        for output_score, output in zip(output_scores, outputs):
            assert len(output_score) == len(output), f"{len(output_score)} != {len(output)}"

        return output_scores

class MyMathShepherd(PRM):
    def load_model_and_tokenizer(self) -> tuple[PreTrainedModel, PreTrainedTokenizer]:
        model_path = str(Path(self.args.prm).resolve())
        logger.info(f"Loading model from {model_path}")
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            device_map=self.args.prm_device,
            attn_implementation="flash_attention_2",
            torch_dtype=torch.float16,
        ).eval()
        tokenizer = AutoTokenizer.from_pretrained(model_path)

        # For batched inference
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.add_special_tokens({"additional_special_tokens": [self.placeholder_token_in_tokenizer] + self.reward_tokens_in_tokenizer})
        logger.info(f"Placeholder token: {self.placeholder_token_in_tokenizer} and reward tokens: {self.reward_tokens_in_tokenizer} added to tokenizer as special tokens")

        self.STEP_TAG_ID = tokenizer.encode(self.placeholder_token_in_tokenizer, add_special_tokens=False)[0]
        self.CANDIDATE_TOKENS = tokenizer.encode(["+", "-"], add_special_tokens=False)
        return model, tokenizer

    def score(self, questions: list[str], outputs: list[list[str]]) -> list[list[list[float]]]:
        placeholder_token = self.placeholder_token
        placeholder_token_in_tokenizer = self.placeholder_token_in_tokenizer
        inputs_for_prm = []
        lengths = []
        for question, output in zip(questions, outputs):
            # prompt = self.search_config.system_prompt + "\n" + question + "\n"
            prompt = question.strip()
            special_outputs = []
            for o in output:
                o = o.replace(placeholder_token, placeholder_token_in_tokenizer)
                if not o.endswith(placeholder_token_in_tokenizer):
                    o = o + placeholder_token_in_tokenizer
                special_outputs.append(o)
                # logger.debug(f"Special output:\n{o}")
            inputs_for_prm.extend([f"{prompt} {o}" for o in special_outputs])
            lengths.append(len(output))

        # TODO: tokenize each batch independently so there is less padding and faster inference
        output_scores = batched_math_shepherd_inference(
            self.model,
            self.tokenizer,
            inputs_for_prm,
            self.args.prm_batch_size,
            self.STEP_TAG_ID,
            self.CANDIDATE_TOKENS,
        )
        # logger.debug(output_scores)
        cumulative_lengths = list(accumulate(lengths))
        # reshape the output scores to match the input
        output_scores = [
            output_scores[i:j]
            for i, j in zip([0] + cumulative_lengths[:-1], cumulative_lengths)
        ]

        # stripped_output_scores = [] TODO: strip out the reward for previous steps
        for output_score, output in zip(output_scores, outputs):
            # for i in range(len(output)):
            #     print(f"{output_score[i]}: {output[i]}")
            assert len(output_score) == len(output), f"{len(output_score)} != {len(output)}"

        return output_scores


def build_PRM(args):
    if args.prm == "random":
        return RandomReward(args)
    elif args.prm == "math-shepherd":
        return MathShepherd(args)
    elif args.prm == "qwen":
        return QwenPRM(args)
    elif args.prm == "rlhfflow":
        return RLHFFlow(args)
    else:
        return MyMathShepherd(args)

def release_vllm(llm: LLM):
    #del a vllm.executor.ray_gpu_executor.RayGPUExecutor object
    del llm.llm_engine.model_executor
    del llm

    import ray
    ray.shutdown()

    import gc
    gc.collect()

    torch.cuda.empty_cache()

MAX_INT = sys.maxsize
INVALID_ANS = "[invalid]"

invalid_outputs = []
def remove_boxed(s):
    left = "\\boxed{"
    try:
        assert s[:len(left)] == left
        assert s[-1] == "}"
        return s[len(left):-1]
    except:
        return None

def extract_answer(completion: str):
    split_ans = completion.split('The answer is: ')
    if len(split_ans) > 1:
        ans = split_ans[-1]
        ans = ans.replace("ки", "")
        extract_ans_temp = ans.split('.\n')[0]
        extract_ans_temp = extract_ans_temp.strip()
        if len(extract_ans_temp)>0 and extract_ans_temp[-1] == '.':
            extract_ans = extract_ans_temp[0:-1]
        else:
            extract_ans = extract_ans_temp
        extract_ans = extract_ans.strip()
        return extract_ans
    else:
        return None


def aggregate_scores(scores: list[float], agg_strategy: Literal["min", "prod", "last"]) -> float:
    if agg_strategy == "min":
        return min(scores)
    elif agg_strategy == "prod":
        return math.prod(scores)
    elif agg_strategy == "last":
        return scores[-1]
    else:
        raise ValueError(f"Invalid aggregation strategy: {agg_strategy}")


def approach_greedy(jsonlist: list[dict[str, str]], llm: LLM, args):
    stop_tokens = [
        "Question:", "Question",
        "USER:", "USER",
        "ASSISTANT:", "ASSISTANT",
        "Instruction:", "Instruction",
        "Response:", "Response",
    ]
    sampling_params = SamplingParams(
        n=1,
        temperature=0.01,  # 调低温度以减少生成文本的随机性
        top_p=1,           # 调整 top_p 以控制采样范围
        max_tokens=args.max_tokens,
        seed=args.seed,
        stop=stop_tokens,
        include_stop_str_in_output=True,
    )
    print('sampleing =====', sampling_params)
    prompts = [item["prompt"] for item in jsonlist]
    completions = llm.generate(prompts, sampling_params)
    for item, output in tqdm(zip(jsonlist, completions)):
        prompt_temp = output.prompt
        generated_text = output.outputs[0].text
        item["predict_output"] = generated_text
    return jsonlist

def approach_outcome_best_of_N(jsonlist: list[dict[str, str]], llm: LLM, args):
    prompts = [item["prompt"] for item in jsonlist]
    questions = [item["instruction"] for item in jsonlist]
    stop_tokens = [
        "Question:", "Question",
        "USER:", "USER",
        "ASSISTANT:", "ASSISTANT",
        "Instruction:", "Instruction",
        "Response:", "Response",
    ]
    sampling_params = SamplingParams(
        n=args.n,
        temperature=args.temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
        # seed=args.seed, # 为了保证采样的多样性，不使用seed
        stop=stop_tokens,
        include_stop_str_in_output=True,
    )
    print('sampleing params'.center(30, "="))
    print(sampling_params)
    print("生成阶段".center(30, "="))
    group_completions = []
    completions = llm.generate(prompts, sampling_params)
    for completion in tqdm(completions):
        n_completions = [output.text for output in completion.outputs]
        group_completions.append(n_completions)
    print("评分阶段".center(30, "="))
    release_vllm(llm)
    prm = build_PRM(args)  # 仅在需要的时候加载奖励模型
    group_scores = prm.score(questions, group_completions)
    for item, completions, scores in tqdm(zip(jsonlist, group_completions, group_scores)):
        outcome_scores = [aggregate_scores(n_scores, args.agg_strategy) for n_scores in scores]
        # 规则奖励：过长、无答案，直接否定
        for i in range(len(outcome_scores)):
            if not extract_answer(completions[i]):
                outcome_scores[i] -= 1
        pred = completions[np.argmax(outcome_scores)]
        item["outcome_scores"] = outcome_scores
        item["predict_output"] = pred
        for i, (completion, n_scores, outcome_score) in enumerate(zip(completions, scores, outcome_scores)):
            item[f"completion_{i}"] = completion
            item[f"process_scores_{i}"] = n_scores
            item[f"outcome_score_{i}"] = outcome_score
    return jsonlist


@dataclass
class Beam:
    prompt: str
    index: int
    current_text: str | None
    next_texts: list[str] | None
    lookahead_texts: list[str] | None
    lookahead_token_ids: list[list[int]] | None
    stop_reasons: list[str | None] | None
    best_scores: list[float]  # the PRM scores
    all_scores: list[list[float]]  # all PRM scores
    previous_text: str | None
    history: list[str]
    history_token_ids: list[list[int]]
    completed: bool = False
    completion_tokens: int = 0


@dataclass
class GenResult:
    index: int
    initial_prompt: str
    first_step_text: str
    first_step_stop_reason: str
    lookahead_text: str
    lookahead_token_ids: list[int]
    stop_reason: str | None


def generate_k_steps(
    prompts: list[str],
    lookahead_steps: int,
    llm: LLM,
    sampling_params: SamplingParams,
    k: int,
) -> list[Beam]:
    gen_results = []
    for i, text in enumerate(prompts):
        for j in range(k):
            gen_result = GenResult(
                index=i,
                initial_prompt=text,
                first_step_text="",
                lookahead_text="",
                lookahead_token_ids=[],
                stop_reason=None,
                first_step_stop_reason=None,
            )
            gen_results.append(gen_result)

    gen_sampling_params = copy.deepcopy(sampling_params)

    for i in range(lookahead_steps + 1):
        if i >= 1:
            gen_sampling_params.temperature = 0.0  # greedy for the rest of the steps
        # get all generations that did not finish with eos
        current_gen = [
            gen_results[i]
            for i in range(len(gen_results))
            if gen_results[i].stop_reason != "EOS"
        ]
        gen_prompts = [
            gen_result.initial_prompt + gen_result.lookahead_text
            for gen_result in current_gen
        ]
        llm_outputs = llm.generate(gen_prompts, gen_sampling_params, use_tqdm=True)
        for gen_result, output in zip(current_gen, llm_outputs):
            gen_text = output.outputs[0].text
            gen_token_ids = output.outputs[0].token_ids
            if i == 0:
                gen_result.first_step_text = gen_text
                gen_result.first_step_stop_reason = output.outputs[0].stop_reason
                if gen_result.first_step_stop_reason is None:
                    gen_result.first_step_stop_reason = "EOS"

            gen_result.lookahead_text = gen_result.lookahead_text + gen_text
            gen_result.lookahead_token_ids = gen_result.lookahead_token_ids + [gen_token_ids]
            gen_result.stop_reason = output.outputs[0].stop_reason
            if gen_result.stop_reason is None:
                gen_result.stop_reason = "EOS"

    outputs: list[Beam] = []

    counter = 0
    for i, text in enumerate(prompts):
        next_texts = []
        stop_reasons = []
        lookahead_texts = []
        lookahead_token_ids = []
        for j in range(k):
            gen_result = gen_results[counter]
            next_texts.append(gen_result.first_step_text)
            lookahead_texts.append(gen_result.lookahead_text)
            lookahead_token_ids.append(gen_result.lookahead_token_ids)
            stop_reasons.append(gen_result.first_step_stop_reason)
            counter += 1

        beam_result = Beam(
            prompt=text,
            index=i,
            current_text="",
            next_texts=next_texts,
            lookahead_texts=lookahead_texts,
            lookahead_token_ids=lookahead_token_ids,
            stop_reasons=stop_reasons,
            best_scores=[0.0],
            all_scores=[],
            previous_text=None,
            history=[],
            history_token_ids=[],
        )
        outputs.append(beam_result)

    return outputs


def approach_process_best_of_N(jsonlist: list[dict[str, str]], llm: LLM, args):
    prm = build_PRM(args)  # 仅在需要的时候加载奖励模型
    n = args.n
    beam_width = args.beam_width
    # Initialize beams
    # At each step, explore n for each activate beam trajectory, then prune to beam_width trajectories.
    # Normally, we select top beam_width of n * beam_width beams.
    # If k of the top beam_width beams are completed, we have beam_width - k beams to be active.
    # Then we have k + (beam_width - k) * n beams, where we select top beam_width beams.
    group_beams: dict[str, list[Beam]] = defaultdict(list)
    for item in jsonlist:
        prompt = item["prompt"]
        for i in range(beam_width):
            b = Beam(
                prompt=prompt,
                index=i,
                current_text="",
                next_texts=None,
                lookahead_texts=None,
                lookahead_token_ids=[],
                completed=False,
                stop_reasons=None,
                history=[],
                best_scores=[],
                all_scores=[],
                previous_text=None,
                completion_tokens=0,
            )
            group_beams[b.prompt].append(b)
    stop_tokens = [
        "Question:", "Question",
        "USER:", "USER",
        "ASSISTANT:", "ASSISTANT",
        "Instruction:", "Instruction",
        "Response:", "Response",
        prm.placeholder_token,
    ]
    sampling_params = SamplingParams(
        n=1,
        temperature=args.temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
        stop=stop_tokens,
        include_stop_str_in_output=True,
    )
    max_steps = args.max_steps
    for step in tqdm(range(max_steps), desc="Beam search iterations"):
        # 1. Explore k completions for each beam (will produce n beams in total)
        # Duplicate active beams to ensure that we have n beams per iteration
        active_beams: list[Beam] = []
        for prompt in group_beams:
            prompt_beams = group_beams[prompt]  # beam_width beams
            prompt_inactivate_beams = []
            prompt_activate_beams = []
            for b in prompt_beams:
                if b.completed:
                    prompt_inactivate_beams.append(b)
                else:
                    # expand active beams
                    for _ in range(n):
                        prompt_activate_beams.append(copy.deepcopy(b))
            active_beams.extend(prompt_activate_beams)
            group_beams[prompt] = prompt_inactivate_beams + prompt_activate_beams

        if len(active_beams) == 0:
            break

        if step == max_steps - 1:
            # Last iteration, generate to EOS
            sampling_params = SamplingParams(
                n=1,
                temperature=args.temperature,
                top_p=args.top_p,
                max_tokens=args.max_tokens,
            )

        # generate n completions for each active beam
        gen_inputs = [b.prompt + b.current_text for b in active_beams]
        lookahead = 0 if i == max_steps - 1 else args.lookahead
        # we have duplicated the active beams before, so here we set k=1
        gen_results = generate_k_steps(gen_inputs, lookahead, llm, sampling_params, k=1)

        prompts, completions = [], []
        for beam, gen_result in zip(active_beams, gen_results, strict=True):
            beam.next_texts = gen_result.next_texts
            beam.stop_reasons = gen_result.stop_reasons
            beam.lookahead_texts = gen_result.lookahead_texts
            beam.lookahead_token_ids = gen_result.lookahead_token_ids
            beam.completion_tokens += gen_result.completion_tokens
            beam.current_text += beam.next_texts[0]
            beam.history.append(beam.next_texts[0])
            beam.history_token_ids.append(beam.lookahead_token_ids[0])

            if (
                beam.stop_reasons[0] == "EOS"
                or beam.stop_reasons[0] == "length"
                or beam.next_texts[0] == ""
            ):
                # collect completed beams
                beam.completed = True
            prompts.append(beam.prompt)
            completions.append([beam.current_text])

        # 2. Score beam_size * n completions
        scores = prm.score(prompts, completions)
        for beam, scores_with_previous_rewards in zip(active_beams, scores, strict=True):
            beam.all_scores.append(scores_with_previous_rewards[0])
            beam.best_scores.append(aggregate_scores(scores_with_previous_rewards[0], args.agg_strategy))

        # Early stopping if all beams are completed
        if len([b for b in active_beams if not b.completed]) == 0:
            break

        # 3. Get top beam_width beams
        for prompt in group_beams:
            prompt_beams = group_beams[prompt]

            # remove duplicate active beams
            if args.remove_duplicates:
                unique_beam_dict = {b.current_text: i for i, b in enumerate(prompt_beams)}
                prompt_beams = [prompt_beams[i] for i in unique_beam_dict.values()]

            assert len(prompt_beams) > 0, f"prompt {prompt} has no active beams"

            # Get indices for top beam_width completions
            agg_scores = []
            for beam in prompt_beams:
                agg_scores.append(beam.best_scores[-1])
            top_indices = np.argsort(np.array(agg_scores).flatten())[-beam_width:]  # top beam_width indices
            top_beams = [prompt_beams[i] for i in list(top_indices)]
            if len(top_beams) < beam_width:
                active_top_beams = [b for b in top_beams if not b.completed]
                if len(active_top_beams) > 0:
                    repeats = math.ceil((beam_width - len(top_beams)) / len(active_top_beams))
                    active_top_beams.extend([copy.deepcopy(b) for b in active_top_beams for _ in range(repeats)])
                top_beams = [b for b in top_beams if b.completed] + active_top_beams
                top_beams = top_beams[:beam_width]
            group_beams[prompt] = top_beams

    # 5. Save results
    for item in jsonlist:
        prompt = item["prompt"]
        item_beams = group_beams[prompt]
        # print(len(item_beams), prompt)
        # for i, b in enumerate(item_beams):
        #     print(f"beam {i}:")
        #     print(b.current_text)
        #     print(aggregate_scores(b.best_scores, args.agg_strategy))
        #     print()
        best_completion_texts = [b.current_text for b in item_beams]
        best_scores = [b.best_scores for b in item_beams]
        best_outcome_scores = [aggregate_scores(s, args.agg_strategy) for s in best_scores]
        best_beam = item_beams[np.argmax(best_outcome_scores)]
        item["selected_prm_scores"] = best_beam.best_scores
        item["predict_output"] = best_beam.current_text
        for i in range(len(item_beams)):
            item[f"completion_{i}"] = best_completion_texts[i]
        for i in range(len(item_beams)):
            item[f"process_scores_{i}"] = best_scores[i]
        for i in range(len(item_beams)):
            item[f"outcome_score_{i}"] = best_outcome_scores[i]

    return jsonlist

def approach_process_with_reflection_best_of_N(jsonlist: list[dict[str, str]], llm: LLM, args):
    prm = build_PRM(args)  # 仅在需要的时候加载奖励模型
    n = args.n
    beam_width = args.beam_width
    # Initialize beams
    # At each step, explore n for each activate beam trajectory, then prune to beam_width trajectories.
    # Normally, we select top beam_width of n * beam_width beams.
    # If k of the top beam_width beams are completed, we have beam_width - k beams to be active.
    # Then we have k + (beam_width - k) * n beams, where we select top beam_width beams.
    group_beams: dict[str, list[Beam]] = defaultdict(list)
    for item in jsonlist:
        prompt = item["prompt"]
        for i in range(beam_width):
            b = Beam(
                prompt=prompt,
                index=i,
                current_text="",
                next_texts=None,
                lookahead_texts=None,
                lookahead_token_ids=None,
                completed=False,
                stop_reasons=None,
                history=[],
                history_token_ids=[],
                best_scores=[],
                all_scores=[],
                previous_text=None,
                completion_tokens=0,
            )
            group_beams[b.prompt].append(b)
    stop_tokens = [
        "Question:", "Question",
        "USER:", "USER",
        "ASSISTANT:", "ASSISTANT",
        "Instruction:", "Instruction",
        "Response:", "Response",
        " " + prm.placeholder_token + "\n",
        prm.placeholder_token + "\n",
        prm.placeholder_token + " ",
        " " + prm.placeholder_token + " ",
        "\\ " + prm.placeholder_token,
        prm.placeholder_token,
    ]
    sampling_params = SamplingParams(
        n=1,
        temperature=args.temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
        stop=stop_tokens,
        include_stop_str_in_output=True,
    )
    max_steps = args.max_steps
    # 优化：每次生成到底，然后再评分，回溯到第一个reward为-的步骤，这样可以减少生成次数
    for step in tqdm(range(max_steps), desc="Beam search iterations"):
        print()
        # 1. Explore k completions for each beam (will produce n beams in total)
        # Duplicate active beams to ensure that we have n beams per iteration
        active_beams: list[Beam] = []
        for prompt in group_beams:
            prompt_beams = group_beams[prompt]  # beam_width beams
            prompt_inactivate_beams = []
            prompt_activate_beams = []
            for b in prompt_beams:
                if b.completed:
                    prompt_inactivate_beams.append(b)
                else:
                    # expand active beams
                    for _ in range(n):
                        prompt_activate_beams.append(copy.deepcopy(b))
            active_beams.extend(prompt_activate_beams)
            group_beams[prompt] = prompt_inactivate_beams + prompt_activate_beams

        if len(active_beams) == 0:
            break

        if step == max_steps - 1:
            # Last iteration, generate to EOS
            sampling_params = SamplingParams(
                n=1,
                temperature=args.temperature,
                top_p=args.top_p,
                max_tokens=args.max_tokens,
            )

        # generate n completions for each active beam
        gen_inputs = []
        for b in active_beams:
            step_str = "Let's reflect on the previous step."
            if len(b.best_scores) == 0:
                pass
            elif len(b.best_scores) == 1:
                if b.best_scores[-1] < 0.5:
                    if step_str not in b.history[-1]:
                        if "Step" in b.history[-1] and " " in b.history[-1]:
                            step_i = b.history[-1].split(": ")[0].strip()
                            num = int(step_i.split(" ")[-1]) if " " in step_i and str.isdigit(step_i.split(" ")[-1]) else None
                            if num:
                                step_str = "Step " + str(num + 1) + ": " + step_str
                            else:
                                step_str = step_i + ": " + step_str
                        suffix = "\n" + step_str
                        b.current_text = b.current_text + suffix
                        b.history[-1] = b.history[-1] + suffix
            else:
                # if b.best_scores[-2] > 0 and (b.best_scores[-1] - b.best_scores[-2]) / b.best_scores[-2] < -0.1:
                if b.best_scores[-1] < 0.5:
                    if step_str not in b.history[-1]:
                        if "Step" in b.history[-1] and " " in b.history[-1]:
                            step_i = b.history[-1].split(": ")[0].strip()
                            num = int(step_i.split(" ")[-1]) if " " in step_i and str.isdigit(step_i.split(" ")[-1]) else None
                            if num:
                                step_str = "Step " + str(num + 1) + ": " + step_str
                            else:
                                step_str = step_i + ": " + step_str
                        suffix = "\n" + step_str
                        b.current_text = b.current_text + suffix
                        b.history[-1] = b.history[-1] + suffix
            gen_inputs.append(b.prompt + b.current_text)
        lookahead = 0 if i == max_steps - 1 else args.lookahead
        # we have duplicated the active beams before, so here we set k=1
        gen_results = generate_k_steps(gen_inputs, lookahead, llm, sampling_params, k=1)

        prompts, completions = [], []
        for beam, gen_result in zip(active_beams, gen_results, strict=True):
            beam.next_texts = gen_result.next_texts
            beam.stop_reasons = gen_result.stop_reasons
            beam.lookahead_texts = gen_result.lookahead_texts
            beam.lookahead_token_ids = gen_result.lookahead_token_ids
            beam.completion_tokens += gen_result.completion_tokens
            if len(gen_result.lookahead_token_ids) > 0 and not isinstance(list(gen_result.lookahead_token_ids)[0], int):
                # logger.warning(f"token_ids is not list of int: {gen_result.lookahead_token_ids}, where text is {gen_result.next_texts}")
                beam.history_token_ids.append(gen_result.lookahead_token_ids[0][0])
                text = llm.get_tokenizer().batch_decode(gen_result.lookahead_token_ids[0][0], skip_special_tokens=True)
                next_text = "".join(text) if isinstance(text, list) else text
                beam.current_text += next_text
                beam.history.append(next_text)
                # if next_text != gen_result.next_texts[0]:
                #     logger.warning(f"next_text is different: {next_text} vs {gen_result.next_texts[0]}")
            else:
                beam.history_token_ids.append(gen_result.lookahead_token_ids[0])
                beam.current_text += beam.next_texts[0]
                beam.history.append(beam.next_texts[0])

            if (
                beam.stop_reasons[0] == "EOS"
                or beam.stop_reasons[0] == "length"
                or beam.next_texts[0] == ""
            ):
                # collect completed beams
                beam.completed = True
            prompts.append(beam.prompt)
            completions.append([beam.current_text])

        # 2. Score beam_size * n completions
        scores = prm.score(prompts, completions)
        for beam, scores_with_previous_rewards in zip(active_beams, scores, strict=True):
            beam.all_scores.append(scores_with_previous_rewards[0])
            beam.best_scores.append(aggregate_scores(scores_with_previous_rewards[0], args.agg_strategy))

        # Early stopping if all beams are completed
        if len([b for b in active_beams if not b.completed]) == 0:
            break

        # 3. Get top beam_width beams
        for prompt in group_beams:
            prompt_beams = group_beams[prompt]

            # remove duplicate active beams
            if args.remove_duplicates:
                unique_beam_dict = {b.current_text: i for i, b in enumerate(prompt_beams)}
                prompt_beams = [prompt_beams[i] for i in unique_beam_dict.values()]

            assert len(prompt_beams) > 0, f"prompt {prompt} has no active beams"

            # Get indices for top beam_width completions
            agg_scores = []
            for beam in prompt_beams:
                agg_scores.append(beam.best_scores[-1])
            top_indices = np.argsort(np.array(agg_scores).flatten())[-beam_width:]  # top beam_width indices
            top_beams = [prompt_beams[i] for i in list(top_indices)]
            if len(top_beams) < beam_width:
                active_top_beams = [b for b in top_beams if not b.completed]
                if len(active_top_beams) > 0:
                    repeats = math.ceil((beam_width - len(top_beams)) / len(active_top_beams))
                    active_top_beams.extend([copy.deepcopy(b) for b in active_top_beams for _ in range(repeats)])
                top_beams = [b for b in top_beams if b.completed] + active_top_beams
                top_beams = top_beams[:beam_width]
            group_beams[prompt] = top_beams

    # 5. Save results
    for item in jsonlist:
        prompt = item["prompt"]
        item_beams = group_beams[prompt]
        # print(len(item_beams), prompt)
        # for i, b in enumerate(item_beams):
        #     print(f"beam {i}:")
        #     print(b.current_text)
        #     print(aggregate_scores(b.best_scores, args.agg_strategy))
        #     print()
        best_completion_texts = [b.current_text for b in item_beams]
        best_scores = [b.best_scores for b in item_beams]
        best_outcome_scores = [aggregate_scores(s, args.agg_strategy) for s in best_scores]
        best_beam = item_beams[np.argmax(best_outcome_scores)]
        item["history"] = best_beam.history
        item["history_token_ids"] = best_beam.history_token_ids
        item["selected_prm_scores"] = best_beam.best_scores[:-1]
        item["predict_output"] = best_beam.current_text
        for i in range(len(item_beams)):
            item[f"completion_{i}"] = best_completion_texts[i]
        for i in range(len(item_beams)):
            item[f"process_scores_{i}"] = best_scores[i]
        for i in range(len(item_beams)):
            item[f"outcome_score_{i}"] = best_outcome_scores[i]

    return jsonlist


def load_MATH(data_file: str, start: int, end: int):
    problem_prompt = (
        "Below is an instruction that describes a task. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\n{instruction}\n\n### Response: Let's think step by step."
    )
    problem_prompt = (
        "{instruction} "
    )
    print('prompt'.center(10, "="))
    print(repr(problem_prompt))
    jsonlist = load_json_or_jsonl(data_file)
    for idx, item in enumerate(jsonlist):
        item["prompt"] = problem_prompt.format(instruction=item["instruction"])
        solution = item['output']
        ground_truth_answer = remove_boxed(util.last_boxed_only_string(solution))
        item['ground_truth_answer'] = ground_truth_answer

    print('total length ===', len(jsonlist))
    jsonlist_subset = jsonlist[start:end]
    print('start===', start, ', end====',end, ', length ===', len(jsonlist_subset))
    return jsonlist_subset

def load_MATH500(data_file: str, start: int, end: int):
    data_file = "/home/linxueyuan/github/o1/LLM/datasets--HuggingFaceH4--MATH-500/snapshots/ff5b20257d8185524591543f8ff5993951537bb8/test.jsonl"
    system_prompt: str = "Solve the following math problem efficiently and clearly:\n\n- For simple problems (2 steps or fewer):\nProvide a concise solution with minimal explanation.\n\n- For complex problems (3 steps or more):\nUse this step-by-step format:\n\n## Step 1: [Concise description]\n[Brief explanation and calculations]\n\n## Step 2: [Concise description]\n[Brief explanation and calculations]\n\n...\n\nRegardless of the approach, always conclude with:\n\nTherefore, the final answer is: $\\boxed{answer}$. I hope it is correct.\n\nWhere [answer] is just the final number or expression that solves the problem."
    problem_prompt = (
        "Below is an instruction that describes a task. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\n{instruction}\n\n### Response: Let's think step by step."
    )
    problem_prompt = (
        "{instruction} "
    )
    print('prompt'.center(10, "="))
    print(repr(problem_prompt))
    jsonlist = load_json_or_jsonl(data_file)
    for idx, item in enumerate(jsonlist):
        item["prompt"] = problem_prompt.format(instruction=item["problem"])
        solution = item['solution']
        ground_truth_answer = remove_boxed(util.last_boxed_only_string(solution))
        item['ground_truth_answer'] = ground_truth_answer

    print('total length ===', len(jsonlist))
    jsonlist_subset = jsonlist[start:end]
    print('start===', start, ', end====',end, ', length ===', len(jsonlist_subset))
    return jsonlist_subset


def test_hendrycks_math(args):
    # 1. Load dataset
    jsonlist_subset = load_MATH(args.data_file, args.start, args.end)

    # 2. Load model
    num_gpus = torch.cuda.device_count()
    llm = LLM(
        model=args.model,
        enable_prefix_caching=True,
        tensor_parallel_size=num_gpus if args.approach in ["greedy", "best_of_N", "outcome_best_of_N"] else num_gpus-1,
    )

    # 3. Test time computation
    test_time_compute_func = {
        "greedy": approach_greedy,
        "best_of_N": approach_outcome_best_of_N,
        "outcome_best_of_N": approach_outcome_best_of_N,
        "beam_search": approach_process_best_of_N,
        "process_best_of_N": approach_process_best_of_N,
        "beam_search_with_reflection": approach_process_with_reflection_best_of_N,
        "process_with_reflection_best_of_N": approach_process_with_reflection_best_of_N,
    }[args.approach]
    jsonlist_subset = test_time_compute_func(jsonlist_subset, llm, args)
    results = []
    for idx, item in enumerate(jsonlist_subset):
        completion = item["predict_output"]
        answer = item["ground_truth_answer"]
        extract_ans = extract_answer(completion)
        if extract_ans is None:
            temp = {'question': item["prompt"], 'output': completion, 'answer': answer}
            invalid_outputs.append(temp)
            res = False
        else:
            item["predict_answer"] = extract_ans
            res = util.is_equiv(extract_ans, answer)
        item["match"] = "right" if res else "wrong"
        results.append(res)
        if idx < 5:
            print()
            print('question'.center(30, "="))
            print(item["prompt"])
            print('predict_output'.center(30, "="))
            print(item["predict_output"])
            if "selected_prm_scores" in item:
                print('score'.center(30, "="))
                print(item["selected_prm_scores"])
            print('ground_truth_answer'.center(30, "="))
            print(item["ground_truth_answer"])
            print('predict_answer'.center(30, "="))
            print(extract_ans, "✅" if res else "❌")
            if "history" in item:
                print('history'.center(30, "="))
                print(item["history"])
            if "history_token_ids" in item:
                print('history_token_ids'.center(30, "="))
                for text, token_ids in zip(item["history"], item["history_token_ids"]):
                    tokens = llm.get_tokenizer().batch_decode(token_ids, skip_special_tokens=False)
                    print(repr(text), tokens)
            print()

    # 4. Save results
    acc = sum(results) / len(results)
    print('len invalid outputs ===', len(invalid_outputs))
    print('length===', len(results), ', acc===', acc)
    overview_df = pd.DataFrame([{"acc": acc, "total_num": len(results), "invalid_num": len(invalid_outputs)} | vars(args)])
    result_df = pd.DataFrame(jsonlist_subset)
    df_dict = {}
    df_dict["overview"] = overview_df
    df_dict["result"] = result_df
    save_df_dict(df_dict, args.output_filepath)

def parse_args():
    parser = argparse.ArgumentParser()
    # model
    parser.add_argument("--model", type=str, required=True)  # model path
    # data
    parser.add_argument("--data_file", type=str, required=True)  # data path
    parser.add_argument("--start", type=int, default=0) #start index
    parser.add_argument("--end", type=int, default=MAX_INT)  # end index
    parser.add_argument("--output_filepath", type=str, default=f"{datetime_str}.xlsx")  # output dir
    # test time computation
    parser.add_argument("--approach", type=str, default='bese_of_n')  # test time compute
    parser.add_argument("--n", type=int, default=4, help="the n of candidates. For beam search, explore n candidates for each beam.")  # test time compute
    parser.add_argument("--agg_strategy", type=str, default='last')  # choose from ['min', 'prod', 'last']
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--top_p", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max_tokens", type=int, default=2048)
    # beam search
    parser.add_argument("--beam_width", type=int, default=4,
                        help="beam width")
    parser.add_argument("--max_steps", type=int, default=8,
                        help="max number of beam search steps")
    parser.add_argument("--lookahead", type=int, default=0,
                        help="number of steps to lookahead")
    parser.add_argument("--sort_completed", action="store_true", default=False,
                        help="sort completed beams by score")
    parser.add_argument("--remove_duplicates", action="store_true", default=False,
                        help="remove duplicate beams")
    # prm
    parser.add_argument("--prm", type=str, default="math-shepherd",
                        help="the path of prm model")
    parser.add_argument("--prm_batch_size", type=int, default=64)
    parser.add_argument("--prm_device", type=str, default="auto")
    parser.add_argument("--placeholder_token", type=str, default=None, help="placeholder token in dataset")
    parser.add_argument("--reward_tokens", type=str, nargs="*", default=None, help="reward tokens in dataset")
    parser.add_argument("--placeholder_token_in_tokenizer", type=str, default=None,
                        help="placeholder_token in dataset will be repalced to reserved token in tokenizer when preprocessing.")
    parser.add_argument("--reward_tokens_in_tokenizer", type=str, nargs="*", default=None,
                        help="reward_tokens in dataset will be repalced to reserved tokens in tokenizer when preprocessing.")

    args = parser.parse_args()

    if args.placeholder_token_in_tokenizer is None:
        args.placeholder_token_in_tokenizer = args.placeholder_token
        print(
            "Option '--placeholder_token_in_tokenizer' is None. "
            f"It is set to the placeholder token {repr(args.placeholder_token)} in dataset by default."
        )
    if args.reward_tokens_in_tokenizer is None:
        args.reward_tokens_in_tokenizer = args.reward_tokens
        print(
            "Option '--reward_tokens_in_tokenizer' is None. "
            f"It is set to the reward tokens {repr(args.reward_tokens)} in dataset by default."
        )
    import json
    print(json.dumps(vars(args), indent=4))
    return args

if __name__ == "__main__":
    args = parse_args()
    test_hendrycks_math(args)