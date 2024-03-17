import subprocess


def create_secret():
    try:
        subprocess.run(
            ['kubectl', 'create', 'secret', 'generic', 'postgres-ssl-key', '--from-file=../root.crt'],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error creating secret: {e}")


if __name__ == "__main__":
    create_secret()
