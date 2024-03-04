import logging
import os
import time
from glob import glob
from pathlib import Path

from yaspin import yaspin
from yaspin.spinners import Spinners

spinner = yaspin(Spinners.dots, color="blue")

with spinner:
    from dotenv import load_dotenv

    import sys

    import inquirer

    from llama_index.llms.openai import OpenAI
    from llama_index.core import Settings
    from llama_index.core import StorageContext
    from llama_index.core import VectorStoreIndex
    from llama_index.core import SimpleDirectoryReader
    from llama_index.core import PromptTemplate
    from llama_index.core import load_index_from_storage

    from llama_index.core.prompts.default_prompts import DEFAULT_REFINE_PROMPT

load_dotenv()

Settings.llm = OpenAI(model="gpt-3.5-turbo")

PATH_TO_PDFS = "pdfs"
PATH_TO_INDEXES = "gpt_indexes"


def pdf_to_index(pdf_path, save_path):
    """
    Converts a PDF document into an index for querying.

    Args:
        pdf_path (str): The file path to the PDF document.
        save_path (str): The directory path where the index should be saved.
    """
    documents = SimpleDirectoryReader(input_files=[Path(pdf_path)]).load_data()

    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=save_path)

    print("\033[0;32mSaved PDF index to disk\033[0m")


def query_index(query_u, pdf_name):
    """
    Queries an existing index with a user's prompt.

    Args:
        query_u (str): The user's query or question.
        pdf_name (str): The name of the PDF document's index to query.
    """
    QA_PROMPT_TMPL = (
        "We have provided context information below. \n"
        "---------------------\n"
        "{context_str}"
        "\n---------------------\n"
        "Given this information above, please answer the question clearly but as concisely as possible: {query_str}\n"
    )
    QA_PROMPT = PromptTemplate(QA_PROMPT_TMPL)

    storage_context = StorageContext.from_defaults(persist_dir=f"{PATH_TO_INDEXES}/{pdf_name}")
    index = load_index_from_storage(storage_context)
    query_engine = index.as_query_engine(streaming=True, text_qa_template=QA_PROMPT)
    response = query_engine.query(query_u)

    return response


def save_pdf(file_path, absolute=False):
    """
    Saves a PDF document by converting it into an index.

    Args:
        file_path (str): The file path to the PDF document.
        absolute (bool, optional): If True, uses the absolute path provided in file_path. 
                                   If False, assumes the file is located in the predefined PDFs directory. 
                                   Defaults to False.
    """
    _, file_name = os.path.split(file_path)

    if absolute:
        pdf_to_index(
            pdf_path=f"{file_path}", save_path=f"{PATH_TO_INDEXES}/{file_name}"
        )
    else:
        pdf_to_index(
            pdf_path=f"{PATH_TO_PDFS}/{file_name}",
            save_path=f"{PATH_TO_INDEXES}/{file_name}",
        )


def setup_directories(directories):
    """
    Ensures that the necessary directories for storing PDFs and their indexes exist.
    If they do not exist, the function creates them.
    """
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)


def prompt_main_menu():
    """
    Displays the main menu to the user and prompts them to choose an action.
    The actions include querying a document, adding a new document, or quitting the application.
    Returns the user's choice.
    """
    menu_questions = [
        inquirer.List(
            "menu_choice",
            message="What would you like to do?",
            choices=["Query a document", "Add a new document", "Quit"],
            carousel=True,
        ),
    ]
    menu_answers = inquirer.prompt(menu_questions, raise_keyboard_interrupt=True)
    return menu_answers.get("menu_choice")


def handle_document_query():
    """
    Handles the user's request to query a document.
    It prompts the user to select a document from the available indexes and then 
    processes the user's queries against the selected document.
    """
    dirs = get_index_directories()
    if not dirs:
        print("\033[0;31mNo PDFs were found\033[0m")
        return

    query_doc_choice = prompt_document_selection(dirs)
    process_queries(query_doc_choice)


def get_index_directories():
    """
    Retrieves a list of directories that contain indexed documents.
    This list is used to present the user with the available documents for querying.
    Returns a list of directory names.
    """
    return [
        d for d in os.listdir(PATH_TO_INDEXES)
        if os.path.isdir(os.path.join(PATH_TO_INDEXES, d))
    ]


def prompt_document_selection(dirs):
    """
    Prompts the user to select a document from the given list of directories.
    Args:
        dirs: A list of directory names containing indexed documents.
    Returns the name of the selected document directory.
    """
    query_doc_questions = [
        inquirer.List(
            "query_doc_choice",
            message="Select a document to query",
            choices=dirs,
            carousel=True,
        ),
    ]
    query_doc_answer = inquirer.prompt(query_doc_questions, raise_keyboard_interrupt=True)
    return query_doc_answer.get("query_doc_choice")


def process_queries(pdf_name):
    """
    Processes user queries against the selected document's index.
    Continuously prompts the user for queries until they decide to exit.
    Args:
        pdf_name: The name of the PDF document to query.
    """
    while True:
        query = input("\033[0;33m> ")
        print("\033[0m", end="")
        if query == "exit":
            break
        elif not query.strip():
            continue
        with spinner:
            res = query_index(query_u=query, pdf_name=pdf_name)
        print_response(res)


def print_response(response):
    """
    Prints the response of a query to the console.
    Args:
        response: The response object containing the answer to a query.
    """
    print("\033[0;36m", end="")
    response.print_response_stream()
    print("\033[0m\n")


def handle_document_addition():
    """
    Handles the user's request to add a new document to the index.
    It prompts the user to select a PDF document or enter a path to a PDF, 
    then indexes the document.
    """
    add_doc_choice = prompt_document_addition()
    if add_doc_choice == "Enter the path to a PDF":
        handle_custom_pdf_path()
    else:
        with spinner:
            save_pdf(add_doc_choice)
        print("Added your PDF")


def prompt_document_addition():
    """
    Prompts the user to select a document to add to the index or to enter a path to a PDF document.
    Args:
        docs: A list of documents available for addition, including an option to enter a path.
    Returns the user's choice.
    """
    docs = glob(os.path.join(PATH_TO_PDFS, "*.pdf"))
    docs.insert(0, "Enter the path to a PDF")
    add_doc_questions = [
        inquirer.List(
            "add_doc_choice",
            message="Select a document to add",
            choices=docs,
            carousel=True,
        ),
    ]
    add_doc_answer = inquirer.prompt(add_doc_questions, raise_keyboard_interrupt=True)
    return add_doc_answer.get("add_doc_choice")


def handle_custom_pdf_path():
    """
    Handles the case where the user chooses to enter a custom path to a PDF document for indexing.
    Prompts the user for the path, validates it, and then proceeds to index the document if valid.
    """
    doc_path = inquirer.prompt(
        [inquirer.Path("doc_path")], raise_keyboard_interrupt=True
    ).get("doc_path")
    if not os.path.isfile(doc_path):
        print("\033[0;31mUnable to find the document.\033[0m")
    else:
        with spinner:
            save_pdf(doc_path, absolute=True)
        print("Added your PDF")


def handle_exit():
    """
    Handles the user's request to exit the application.
    Performs any necessary cleanup before exiting.
    """
    print("\033[0m")
    sys.exit()


def main():
    """
    The main entry point of the application.
    It sets up the necessary directories, 
    then enters a loop to prompt the user with the main menu and 
    handle their choices until they decide to exit.
    """
    setup_directories([PATH_TO_INDEXES, PATH_TO_PDFS])

    try:
        while True:
            menu_choice = prompt_main_menu()
            if menu_choice == "Quit":
                break
            elif menu_choice == "Query a document":
                handle_document_query()
            elif menu_choice == "Add a new document":
                handle_document_addition()
    except KeyboardInterrupt:
        handle_exit()
    except Exception as e:
        raise e


if __name__ == "__main__":
    main()
