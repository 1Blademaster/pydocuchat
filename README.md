# Pydocuchat

Ask questions to your PDF documents using OpenAI's GPT-3.5-turbo.

![Example](https://github.com/1Blademaster/pydocuchat/blob/main/example.gif?raw=true)

## Installation

### Setting up the code

- clone the repository with `git clone https://github.com/1Blademaster/pydocuchat.git`
- cd into the repository with `cd pydocuchat`
- install the requirements with `python -m pip install -r requirements.txt`

### Adding the OpenAI API key

Create a `.env` file by using `cp .example.env .env`, then inside the environment file, you can add your OpenAI API key which you can get from [here](https://platform.openai.com/account/api-keys). **DO NOT SHARE YOUR API KEY WITH ANYONE**.

Note: In order to ask more than 3 questions a minute, you will have to create a billing account with OpenAI. This can be done on the same dashboard where you obtained your API key from. You may get rate-limited within 48 hours of setting up the billing account, however after the first 48 hours everything should be fine.

## Usage

Simply run `python pydocuchat.py` to start adding PDFs.

In the menu, select "Add a PDF", from there you can either input the full path to a PDF document, or place your PDF's in a folder called `pdfs` within the main `pydocuchat` folder. Depending on the size of your PDF, this may take some time.

Then you can start asking questions by selecting a PDF and typing into the terminal.

## Contributing

Contributions are always welcome!

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement". Don't forget to give the project a star! Thanks again!

- Fork the Project
- Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
- Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
- Push to the Branch (`git push origin feature/AmazingFeature`)
- Open a Pull Request

## License

This code is distributed under the [Apache-2.0](https://choosealicense.com/licenses/apache-2.0/) license. See `LICENSE` for more information.
