# flake8: noqa: E501
import base64
import enum
import io
import json
import logging
import time
from typing import Dict

from dojo_sdk_core.types import Action, DoneAction, WaitAction
from dojo_sdk_core.ws_types import HistoryStep
from openai import OpenAI
from PIL import Image

from .basic_cua import BasicCUA
from .computer_use_tool import computer_tool, computer_tool_openai_definition

logger = logging.getLogger(__name__)

logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


class ThinkingType(enum.Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    AUTO = "auto"


THINKING_PROMPT_BASE = """
You should begin by detailing the internal reasoning process, and then present the answer to the user. The reasoning process should be enclosed within <think_never_used_51bce0c785ca2f68081bfa7d91973934> and </think_never_used_51bce0c785ca2f68081bfa7d91973934> tags, as follows:
<think_never_used_51bce0c785ca2f68081bfa7d91973934> reasoning process here </think_never_used_51bce0c785ca2f68081bfa7d91973934> answer here.
You have different modes of thinking:
Unrestricted think mode: Engage in an internal thinking process with thorough reasoning and reflections. You have an unlimited budget for thinking tokens and can continue thinking until you fully solve the problem.
Efficient think mode: Provide a concise internal thinking process with efficient reasoning and reflections. You don't have a strict token budget but be less verbose and more direct in your thinking.
No think mode: Respond directly to the question without any internal reasoning process or extra thinking tokens. Still follow the template with the minimum required thinking tokens to justify the answer.
Budgeted think mode: Limit your internal reasoning and reflections to stay within the specified token budget
Based on the complexity of the problem, select the appropriate mode for reasoning among the provided options listed below.
Provided Mode(s):
{mode}
"""

SYSTEM_PROMPT = """
You are an AI assistant that can control the computer using a mouse and keyboard.

Key guidelines:
- You cannot ask for a screenshot, the user will always provide a screenshot as input
- Use precise coordinates for mouse actions
- Type text when needed for input fields
- Use keyboard shortcuts efficiently
- Complete tasks step by step
- If a task is complete or impossible, use the appropriate action
- Do not prompt the user for any information, just take actions
- You can reflect on your previous thoughts to see what actions you have taken and what you have not taken
- You are an autonomous agent, you do not need to ask the user for any action or confirmation
- YOU CANNOT TAKE A SCREENSHOT, THE USER WILL ALWAYS PROVIDE A SCREENSHOT AS INPUT

You have access to these tools:
- computer_tool: For performing mouse and keyboard actions
"""


class ThinkingMode(enum.Enum):
    NO_THINK = "NO_THINK"
    UNRESTRICTED_THINK = "UNRESTRICTED_THINK"


class SeedCUA(BasicCUA):
    def __init__(
        self,
        model: str,
        api_key: str,
        base_url: str,
        thinking_mode: ThinkingMode = ThinkingMode.NO_THINK,
        image_context_length: int = 3,
        max_tokens: int = 4096,
        system_prompt_suffix: str = "",
        screen_size: tuple[int, int] = (1280, 800),
        verbose: bool = False,
    ):
        super().__init__(
            image_context_length=image_context_length,
            max_tokens=max_tokens,
            system_prompt_suffix=system_prompt_suffix,
            screen_size=screen_size,
            verbose=verbose,
        )
        self.provider = "seed"
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.thinking_mode = thinking_mode
        self.model_screen_size = (1000, 1000)

        self.client = OpenAI(api_key=api_key, base_url=base_url)

        # OpenAI tool definition for computer_tool function
        self.tool_definition = computer_tool_openai_definition()

        if self.verbose:
            logger.info(f"CustomCUA initialized with model: {model}, image_context_length: {image_context_length}")

    def history_to_messages(
        self, history: list[HistoryStep], current_obs: Dict = None, task_instruction: str = None
    ) -> list[dict]:
        """Convert history steps to OpenAI message format, handling tool calls and results.

        Only includes screenshots for the most recent `image_context_length` steps to avoid
        exceeding token limits. Older steps get text only.

        Args:
            history: List of historical steps
            current_obs: Current observation containing the screenshot
            task_instruction: The task instruction to include with the current screenshot
        """
        messages = []
        total_steps = len(history)

        for i, step in enumerate(history):
            # Only include actual images for the most recent steps
            include_image = (total_steps - i) < self.image_context_length

            tool_call_id = self._get_previous_tool_call_id(history, i)

            # Add tool result (text only) and screenshot as user message
            if tool_call_id:
                # Check if last tool call failed
                if step.raw_response and "tool_call_err" in json.loads(step.raw_response):
                    tool_result_content = json.loads(step.raw_response)["tool_call_err"]
                else:
                    tool_result_content = "Action executed successfully."
                # Tool result is always text-only
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": tool_result_content,
                    }
                )
                # Add screenshot as user message if within context window
                if include_image:
                    screenshot_base64 = self._get_cached_image(step.after_screenshot)
                    messages.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/png;base64,{screenshot_base64}"},
                                }
                            ],
                        }
                    )
            else:
                # No tool call - add screenshot as user message
                if include_image:
                    screenshot_base64 = self._get_cached_image(step.after_screenshot)
                    messages.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/png;base64,{screenshot_base64}"},
                                }
                            ],
                        }
                    )

            # Add assistant message from raw response
            if step.raw_response:
                assistant_message = self._parse_assistant_message(step)
                if assistant_message:
                    messages.append(assistant_message)

        # Handle current observation and add screenshot
        if current_obs and "screenshot" in current_obs:
            screenshot = current_obs["screenshot"]
            resized = screenshot.resize(self.screen_size, Image.Resampling.LANCZOS)

            buffer = io.BytesIO()
            resized.save(buffer, format="PNG")
            screenshot_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

            if not messages:
                content = [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_base64}"}},
                ]
                if task_instruction:
                    content.append({"type": "text", "text": task_instruction})
                messages.append({"role": "user", "content": content})
            # Add tool result if previous message had tool call without result
            elif messages[-1]["role"] == "assistant":
                tool_calls = messages[-1].get("tool_calls")
                if tool_calls:
                    tool_call_id = tool_calls[0]["id"]

                    # Check if tool result already exists
                    has_result = any(msg.get("role") == "tool" and msg.get("tool_call_id") == tool_call_id for msg in messages)
                    if not has_result:
                        # Check if the previous tool call had wrong formatting
                        if history and history[-1].raw_response and "tool_call_err" in json.loads(history[-1].raw_response):
                            tool_result_content = json.loads(history[-1].raw_response)["tool_call_err"]
                        else:
                            tool_result_content = "Action executed successfully."
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call_id,
                                "content": tool_result_content,
                            }
                        )
                        content = [
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_base64}"}},
                        ]
                        if task_instruction:
                            content.append({"type": "text", "text": task_instruction})
                        messages.append({"role": "user", "content": content})

        return messages

    def _get_previous_tool_call_id(self, history: list[HistoryStep], current_index: int) -> str | None:
        """Extract tool call ID from previous step's raw response."""
        if current_index == 0:
            return None

        prev_step = history[current_index - 1]
        if not prev_step.raw_response:
            return None

        try:
            prev_raw_data = json.loads(prev_step.raw_response)
            message = prev_raw_data.get("choices", [{}])[0].get("message", {})
            tool_calls = message.get("tool_calls", [])
            return tool_calls[0]["id"] if tool_calls else None
        except (json.JSONDecodeError, KeyError, IndexError):
            return None

    def _parse_assistant_message(self, step: HistoryStep) -> dict | None:
        """Parse assistant message from raw response."""
        try:
            raw_data = json.loads(step.raw_response)

            if "choices" not in raw_data or not raw_data["choices"]:
                logger.error(f"No choices found in raw_response for step {step.step}")
                return None

            message = raw_data["choices"][0]["message"]
            assistant_message = {
                "role": message["role"],
                "content": message.get("content", ""),
            }

            if "tool_calls" in message:
                assistant_message["tool_calls"] = message["tool_calls"]

            return assistant_message
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse raw_response for step {step.step}: {e}")
            return None

    def get_next_action(self, prompt: str, image: Image.Image, history: list) -> tuple[Action, str, str]:
        """Get the next action to take based on the current state."""
        try:
            obs = {"screenshot": image}
            trimmed_history = self._trim_history_to_context_window(history)
            messages = self.history_to_messages(trimmed_history, current_obs=obs, task_instruction=prompt)
            reasoning, actions, raw_response = self.predict(messages)

            if self.verbose:
                logger.info(f"\nPREDICT OUTPUT\n{'=' * 32}\nREASONING: {reasoning}\nACTIONS: {actions}\n")

            if not actions:
                raise ValueError("No actions provided")

            # Calculate scale factors from model's screen size to original image size
            original_width, original_height = image.size
            scale_x = original_width / self.model_screen_size[0]
            scale_y = original_height / self.model_screen_size[1]

            # Convert first action to Dojo Action format
            action_data = actions[0]

            if isinstance(action_data, str):
                if action_data == "DONE":
                    return DoneAction(), reasoning, raw_response
                elif action_data == "WAIT":
                    return WaitAction(seconds=1), reasoning, raw_response
                else:
                    raise ValueError(f"Unknown action: {action_data}")

            if isinstance(action_data, dict):
                action_type = action_data.get("action", "")

                if action_type == "wait":
                    duration = action_data.get("duration", 1)
                    return WaitAction(seconds=duration), reasoning, raw_response

                # Scale coordinates from model's reference frame to original screen size
                action_data = self._scale_coordinates(action_data, scale_x, scale_y)

                try:
                    return computer_tool(**action_data), reasoning, raw_response
                except ValueError as e:
                    if "Screenshot" in str(e):
                        return self.get_next_action(prompt, image, history)

                    # Handle unsupported action
                    unsupported_msg = f"Action '{action_type}' is not supported. Please use a different action."
                    logger.warning(f"Unsupported action: {action_type}. Returning wait action.")
                    combined_reasoning = f"{reasoning}\n\n[SYSTEM: {unsupported_msg}]" if reasoning else unsupported_msg
                    return WaitAction(seconds=1), combined_reasoning, raw_response

        except Exception as e:
            raise ValueError(f"Error in get_next_action: {e}") from e

    def _scale_coordinates(self, action_data: dict, scale_x: float, scale_y: float) -> dict:
        """Scale coordinates from model's reference frame to original screen size."""
        scaled = action_data.copy()

        if "coordinate" in scaled and scaled["coordinate"]:
            scaled["coordinate"] = [
                int(scaled["coordinate"][0] * scale_x),
                int(scaled["coordinate"][1] * scale_y),
            ]

        if "start_coordinate" in scaled and scaled["start_coordinate"]:
            scaled["start_coordinate"] = [
                int(scaled["start_coordinate"][0] * scale_x),
                int(scaled["start_coordinate"][1] * scale_y),
            ]

        return scaled

    def predict(
        self,
        messages: list[dict],
    ):
        """Make a prediction using the OpenAI API.

        Args:
            messages: List of messages in OpenAI format (already processed with screenshots)

        Returns:
            tuple: (reasoning, actions, raw_response)
        """
        if self.thinking_mode.value == ThinkingMode.NO_THINK.value:
            thinking_prompt = THINKING_PROMPT_BASE.format(mode="No think")
        elif self.thinking_mode.value == ThinkingMode.UNRESTRICTED_THINK.value:
            thinking_prompt = THINKING_PROMPT_BASE.format(mode="Unrestricted think")
        else:
            raise ValueError(f"Invalid thinking mode: {self.thinking_mode}")

        # Build system prompt
        system_content = f"{thinking_prompt}\n\n{SYSTEM_PROMPT}"
        if self.system_prompt_suffix:
            system_content += f" {self.system_prompt_suffix}"

        # Prepare final messages with system prompt
        final_messages = [{"role": "system", "content": system_content}] + messages

        try:
            now = time.time()
            attempts = 1
            while True:
                if self.verbose and attempts > 1:
                    logger.info(f"Attempt {attempts} for predict request. Retrying...")

                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=final_messages,
                        max_tokens=self.max_tokens,
                        tools=[self.tool_definition],
                        tool_choice="auto",
                        extra_body={"thinking": {"type": ThinkingType.DISABLED.value}},
                        timeout=120,
                    )
                    break
                except TimeoutError as e:
                    logger.error(f"Timeout in predict: {e}")
                    attempts += 1
                    if attempts > 3:
                        raise ValueError("Error in predict: Maximum number of attempts reached") from e
                    time.sleep(2 * attempts)

            if self.verbose:
                logger.info(f"Predict took {time.time() - now:.2f} seconds")

            message = response.choices[0].message

            # Extract reasoning and actions
            reasoning = message.content or ""
            actions, tool_call_err = self._extract_actions_from_message(message)

            # Build raw_response with parse error if present
            raw_response_dict = response.model_dump()
            if tool_call_err:
                raw_response_dict["tool_call_err"] = tool_call_err
                logger.info(f"Added tool_call_err to raw_response: {tool_call_err}")
            raw_response = json.dumps(raw_response_dict)

            return reasoning, actions, raw_response

        except Exception as e:
            logger.error(f"Error in predict: {e}")
            raise ValueError(f"Error in predict: {e}") from e

    def _extract_actions_from_message(self, message) -> tuple[list, str | None]:
        """Extract actions from tool calls in the message.

        Returns:
            tuple: (actions, error_message) where error_message is None if successful
        """
        actions = []
        error_message = None

        if message.tool_calls:
            for tool_call in message.tool_calls:
                if tool_call.function.name == "computer_tool":
                    try:
                        args = json.loads(tool_call.function.arguments)
                        actions.append(args)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Model returned malformed JSON, attempting repair: {e}")
                        repaired_args = self._repair_tool_arguments(tool_call.function.arguments)
                        if repaired_args:
                            actions.append(repaired_args)
                        else:
                            # Properly encode error details, especially for empty strings
                            raw_args = tool_call.function.arguments
                            if not raw_args or raw_args.strip() == "":
                                error_details = "(empty string)"
                            elif len(raw_args) > 200:
                                error_details = repr(raw_args[:200]) + "... (truncated)"
                            else:
                                error_details = repr(raw_args)

                            error_message = f"Failed to parse action from message. Invalid tool call arguments that could not be repaired: {error_details}. Defaulting to WAIT action."
                            logger.error(f"Failed to repair tool call arguments: {error_details}")

        return (actions or ["WAIT"], error_message)
