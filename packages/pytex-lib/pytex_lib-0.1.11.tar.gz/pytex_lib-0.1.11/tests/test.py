from pathlib import Path
from pytex_lib import write_to_latex


@write_to_latex(file_path=Path(__file__).parent / 'test.tex', keyword="keyword in latex doc")
def get_output(answer: str):
    return answer

if __name__ == "__main__":

    # Answer to be written to the latex doc
    answer = "Response from python script1234."

    # Call the test function 
    get_output(answer)
