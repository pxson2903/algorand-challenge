# Setup Holder Application (Algorand challenge)

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. Install [Algorand sandbox](https://github.com/algorand/sandbox)
3. Start sandbox:
    ```txt
    $ ./sandbox up
    ```
4. Install Python virtual environment in project folder:
    ```txt
    $ python3 -m venv venv
    $ source ./venv/Scripts/activate # Windows
    $ source ./venv/bin/activate # Linux
    $ pip install -r requirements.txt
    ```
5. Build smart contract
    ```txt
    $ python3 11-define_programs.py
    ```
6. Deploy smart contract
    ```txt
    $ python3 12-deploy_application.py
    ```
7. Get basic information
    ```txt
    $ python3 13-call_holder_app.py
    ```