import argparse
import base64
import os


def parse_dev_path():
    parser_dev_path = argparse.ArgumentParser(
        description='Создание k8s сеекрета манифеста'
    )
    parser_dev_path.add_argument('-p', '--path', help='Путь к директории с dev манифестами', default='')

    path_args = parser_dev_path.parse_args()
    return path_args.path


def read_env():
    env_vars = {}
    with open('.env', 'r') as file:
        for variable in file:
            key, value = variable.strip().split('=', 1)
            env_vars[key] = base64.b64encode(value.encode()).decode()
    return env_vars


def write_k8s_manifest(path):
    encoded_vars = read_env()
    file_directory = os.path.join(path, 'django-secret.yaml')
    with open(file_directory, 'w') as f:
        f.write('apiVersion: v1\n')
        f.write('kind: Secret\n')
        f.write('metadata:\n')
        f.write('  name: django-secret\n')
        f.write('type: Opaque\n')
        f.write('data:\n')
        for key, value in encoded_vars.items():
            f.write(f'  {key}: {value}\n')


def main():
    dev_path = parse_dev_path()
    write_k8s_manifest(dev_path)
    print('Ваши данные из .env файла были успешно добавлены в манифест')


if __name__ == '__main__':
    main()
