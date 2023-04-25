import random
import time

import gradio as gr
import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "flaky: mark test as flaky. Failure will not cause te"
    )


@pytest.fixture
def calculator():
    def calculator(num1, operation, num2):
        if operation == "add":
            return num1 + num2
        elif operation == "subtract":
            return num1 - num2
        elif operation == "multiply":
            return num1 * num2
        elif operation == "divide":
            if num2 == 0:
                raise gr.Error("Cannot divide by zero!")
            return num1 / num2

    demo = gr.Interface(
        calculator,
        ["number", gr.Radio(["add", "subtract", "multiply", "divide"]), "number"],
        "number",
        examples=[
            [5, "add", 3],
            [4, "divide", 2],
            [-4, "multiply", 2.5],
            [0, "subtract", 1.2],
        ],
    )
    return demo.queue()


@pytest.fixture
def increment():
    with gr.Blocks() as demo:
        btn1 = gr.Button("Increment")
        btn2 = gr.Button("Increment")
        numb = gr.Number()

        state = gr.State(0)

        btn1.click(
            lambda x: (x + 1, x + 1),
            state,
            [state, numb],
            api_name="increment_with_queue",
        )
        btn2.click(
            lambda x: (x + 1, x + 1),
            state,
            [state, numb],
            queue=False,
            api_name="increment_without_queue",
        )
    return demo.queue()


@pytest.fixture
def progress():
    def my_function(x, progress=gr.Progress()):
        progress(0, desc="Starting...")
        for _ in progress.tqdm(range(20)):
            time.sleep(0.1)
        return x

    return gr.Interface(my_function, gr.Textbox(), gr.Textbox()).queue()


@pytest.fixture
def yield_demo():
    def spell(x):
        for i in range(len(x)):
            time.sleep(0.5)
            yield x[:i]

    return gr.Interface(spell, "textbox", "textbox").queue()


@pytest.fixture
def cancel_from_client():
    def iteration():
        for i in range(20):
            print(f"i: {i}")
            yield i
            time.sleep(0.5)

    def long_process():
        time.sleep(10)
        print("DONE!")
        return 10

    with gr.Blocks() as demo:
        num = gr.Number()

        btn = gr.Button(value="Iterate")
        btn.click(iteration, None, num, api_name="iterate")
        btn2 = gr.Button(value="Long Process")
        btn2.click(long_process, None, num, api_name="long")

    return demo.queue(concurrency_count=40)


@pytest.fixture
def sentiment_classification():
    def classifier(text):
        return {label: random.random() for label in ["POSITIVE", "NEGATIVE", "NEUTRAL"]}

    def sleep_for_test():
        time.sleep(10)
        return 2

    with gr.Blocks(theme="gstaff/xkcd") as demo:
        with gr.Row():
            with gr.Column():
                input_text = gr.Textbox(label="Input Text")
                with gr.Row():
                    classify = gr.Button("Classify Sentiment")
            with gr.Column():
                label = gr.Label(label="Predicted Sentiment")
            number = gr.Number()
            btn = gr.Button("Sleep then print")
        classify.click(classifier, input_text, label, api_name="classify")
        btn.click(sleep_for_test, None, number, api_name="sleep")

    return demo


@pytest.fixture
def count_generator():
    def count(n):
        for i in range(int(n)):
            time.sleep(0.5)
            yield i

    def show(n):
        return str(list(range(int(n))))

    with gr.Blocks() as demo:
        with gr.Column():
            num = gr.Number(value=10)
            with gr.Row():
                count_btn = gr.Button("Count")
                list_btn = gr.Button("List")
        with gr.Column():
            out = gr.Textbox()

        count_btn.click(count, num, out)
        list_btn.click(show, num, out)

    return demo.queue()
