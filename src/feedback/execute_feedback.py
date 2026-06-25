from src.executor import run_executor


def main():
    run_executor(
        input_file="outputs/feedback/refined_tests.json",
        output_file="outputs/feedback/execution_results.json",
        test_key="refined_test",
    )


if __name__ == "__main__":
    main()