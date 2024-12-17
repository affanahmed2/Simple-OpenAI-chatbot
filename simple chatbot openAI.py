import os
from openai import OpenAI
import time
from pathlib import Path

api_key = ""

assistant_id    = ""

def load_openai_client_and_assistant():
    client          = OpenAI(api_key=api_key)
    my_assistant    = client.beta.assistants.retrieve(assistant_id)
    thread          = client.beta.threads.create()

    return client , my_assistant, thread

client,  my_assistant, assistant_thread = load_openai_client_and_assistant()

file = client.files.create(
    file=Path(""),
    purpose='vision',
)


# check in loop  if assistant ai parse our request
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run


# give an image to assistant
def first_response():
  message = client.beta.threads.messages.create(
  thread_id=assistant_thread.id,
  role="user",
  content=[
      {"type": "text", "text": "What is shown in this picture?"},
      {
          "type": "image_file",
          "image_file": {
              "file_id": file.id
          }
      }
        ],
  )

  run = client.beta.threads.runs.create(
        thread_id=assistant_thread.id,
        assistant_id=assistant_id,
    )

  run = wait_on_run(run, assistant_thread)

  # Retrieve all the messages added after our last user message
  messages = client.beta.threads.messages.list(
        thread_id=assistant_thread.id, order="asc", after=message.id
    )

  return messages.data[0].content[0].text.value

# initiate assistant ai response
def get_assistant_response(user_input=""):
    message = client.beta.threads.messages.create(
        thread_id=assistant_thread.id,
        role="user",
        content=user_input,
    )

    run = client.beta.threads.runs.create(
        thread_id=assistant_thread.id,
        assistant_id=assistant_id,
    )

    run = wait_on_run(run, assistant_thread)

    # Check if the assistant triggered a function call


    # Continue normal message handling
    messages = client.beta.threads.messages.list(
        thread_id=assistant_thread.id, order="asc", after=message.id
    )

    return messages.data[0].content[0].text.value


result = first_response()
print(result)

user_input = input()
while user_input:
    result = get_assistant_response(user_input)
    print(result)
    user_input = input()