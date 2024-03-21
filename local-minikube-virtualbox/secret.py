import base64


def read_env():
    env_vars = {}
    with open('../.env', 'r') as file:
        for variable in file:
            key, value = variable.strip().split('=', 1)
            env_vars[key] = base64.b64encode(value.encode()).decode()
    return env_vars


def write_k8s_manifest():
    encoded_vars = read_env()
    with open('django-secret.yaml', 'w') as f:
        f.write('apiVersion: v1\n')
        f.write('kind: Secret\n')
        f.write('metadata:\n')
        f.write('  name: django-secret\n')
        f.write('type: Opaque\n')
        f.write('data:\n')
        for key, value in encoded_vars.items():
            f.write(f'  {key}: {value}\n')


def main():
    write_k8s_manifest()
    print('Ваши данные из .env файла были успешно добавлены в манифест')


if __name__ == '__main__':
    main()
