# appstore-review-llm

This project leverages the power of Large Language Models (LLMs) to analyze and extract valuable insights from app store reviews. By combining state-of-the-art natural language processing capabilities with human oversight, it aims to provide app developers with a comprehensive understanding of user feedback, addressing the challenges posed by the vast volume, diversity, and subjectivity of app reviews.



## Getting Started

```
git clone git@ssh.gitlab.aws.dev:wsuam/appstore-review-llm
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

mkdir output
mkdir upload

python appreviews.py -h
usage: appreviews.py [-h] [-i] [app_name]

Process app name and get reviews summary.

positional arguments:
  app_name           The name of the app to analyze

options:
  -h, --help         show this help message and exit
  -i, --interaction  Enable interactive mode
  

#command line example
python appreviews.py --app_name TikTok
python appreviews.py -i #交互式访问

#use UI
streamlit run main.py

```





## Contributing

We welcome contributions to improve this project! If you encounter any issues or have suggestions for new features, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](./LICENSE).

## Acknowledgments

We would like to express our gratitude to the open-source community and the developers of the LLM services used in this project.
