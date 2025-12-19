import copy
from pathlib import Path
import pickle

from pydantic import BaseModel
from verl import DataProto
from verl.utils import hf_processor, hf_tokenizer
from transformers import PreTrainedTokenizer
from omegaconf import DictConfig

from agentlin.core.types import TaskRolloutEvent
from agentlin.rollout.trajectory import Trajectory
from agentlin.rollout.trajectory_sampler import TrajectorySampler
from agentlin.route.agent_config import AgentConfig


class AgentWorkerConfig(BaseModel):
    uuid: str
    task_name: str
    agent: AgentConfig
    rollout_save_dir: str

    @classmethod
    def from_dictconfig(cls, config: DictConfig) -> "AgentWorkerConfig":
        return cls(
            uuid=config.uuid,
            task_name=config.task_name,
            agent=config.agent,
            rollout_save_dir=config.rollout_save_dir,
        )


class AgentSampler(TrajectorySampler):
    def __init__(self, config: DictConfig):
        super().__init__(config)
        self.config = config
        self.tokenizer: PreTrainedTokenizer = hf_tokenizer(self.config.model_id, trust_remote_code=True)
        self.processor = hf_processor(self.config.model_id, use_fast=True)

    def convert_step_to_token_ids(self, step: TaskRolloutEvent) -> dict[str, list[int]]:
        """Convert an TaskRolloutEvent to token IDs for both prompt and response.

        Args:
            step: The agent step to convert

        Returns:
            Dict containing prompt and response token IDs
        """
        # Convert state messages to prompt
        prompt_messages = []
        for msg in step.input_messages:
            if isinstance(msg["content"], str):
                prompt_messages.append({"role": msg["role"], "content": msg["content"]})
            else:
                content_list = msg["content"]
                for content in content_list:
                    if content["type"] == "text":
                        prompt_messages.append({"role": msg["role"], "content": content["text"]})

        model_inputs = self.tokenizer.apply_chat_template(
            prompt_messages,
            tokenize=True,
            return_dict=True,
            add_generation_prompt=True,
            add_special_tokens=False,
            truncation=True,
            padding="max_length",
            padding_side="left",
            max_length=self.config.agent.max_model_length - self.config.agent.max_response_length,
            return_attention_mask=True,
        )
        prompts_ids = model_inputs["input_ids"]
        attention_mask = model_inputs["attention_mask"]

        response = step.output_messages
        response_output = self.tokenizer(
            response,
            add_special_tokens=False,
            truncation=True,
            padding="max_length",
            max_length=self.config.agent.max_response_length,
        )
        task_ids = response_output["input_ids"]
        input_ids = prompts_ids + task_ids
        attention_mask = attention_mask + response_output["attention_mask"]
        return {
            "prompts": prompts_ids,
            "input_ids": input_ids,
            "task_ids": task_ids,
            "attention_mask": attention_mask,
        }

    def pre_process(self, batch: DataProto) -> list[DictConfig]:
        configs = []

        for i in range(len(batch.non_tensor_batch["question"])):
            config_dict = copy.deepcopy(self.config.agent)
            config_dict.task_name = batch.non_tensor_batch["question"][i]
            config_dict.uuid = batch.non_tensor_batch["uuids"][i]
            config = AgentWorkerConfig.from_dictconfig(config_dict)
            configs.append(config)

        return configs

    def post_process(self, config: type[DictConfig]) -> tuple[dict[str, list]]:
        """Post-process the trajectory data from the agent worker.

        Args:
            config: Configuration object for the agent worker

        Returns:
            Processed tensor and non-tensor trajectory data
        """
        traj_file = Path(config.rollout_save_dir) / f"{config.uuid}.jsonl"

        # Initialize lists to collect all token IDs
        tensor_data = {
            "max_prompt_length": [],
            "prompts": [],
            "input_ids": [],
            "responses": [],
            "attention_mask": [],
        }
        non_tensor_data = {
            "nb_steps": [],
            "meta_info": [],
        }

        trajectory = Trajectory.from_jsonl(traj_file)
        traj: list[TaskRolloutEvent] = trajectory.steps
        meta: list[dict] = [step.meta for step in traj]
        non_tensor_data["meta_info"].extend(meta)

        # Process each step in the trajectory
        for step in traj:
            # Convert step to token IDs
            token_ids = self.convert_step_to_token_ids(step)
            tensor_data["prompts"].append(token_ids["prompts"])
            tensor_data["input_ids"].append(token_ids["input_ids"])
            tensor_data["responses"].append(token_ids["task_ids"])
            tensor_data["attention_mask"].append(token_ids["attention_mask"])
            tensor_data["max_prompt_length"].append(self.config.agent.max_model_length - self.config.agent.max_response_length)
            non_tensor_data["nb_steps"].append(step)

        return tensor_data, non_tensor_data

    def create_running_cmd(self, config: DictConfig) -> list[str]:
        return ""

    def _get_sampled_data_str(self, tensor_data: dict[str, list], non_tensor_data: dict[str, list]) -> str:  # noqa: ARG002
        formatted_str = ""
        state = non_tensor_data["nb_steps"][-1].state
        for message in state:
            formatted_str += f"{message['role'].capitalize()}\n: {message['content'][0]['text']}\n"
        return formatted_str
