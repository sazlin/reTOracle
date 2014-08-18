import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('env', choices=['Prod', 'Test'], default='Test')
ARGS = parser.parse_args()


def create_uwsgi_env_string():
    retval = []
    retval.append(''.join(['R_DB_HOST', '=', os.environ.get('R_DB_HOST')]))
    retval.append(''.join(['R_DB_NAME', '=', os.environ['R_DB_NAME']]))
    retval.append(''.join(['R_DB_USERNAME', '=', os.environ['R_DB_USERNAME']]))
    retval.append(''.join(['R_DB_PASSWORD', '=', os.environ['R_DB_PASSWORD']]))
    retval.append(''.join(['R_HOST', '=', os.environ['R_HOST']]))
    retval.append(''.join(['R_HOST_INSTANCE_ID', '=', os.environ['R_HOST_INSTANCE_ID']]))
    retval.append(''.join(['R_TWITTER_CONSUMER_SECRET', '=', os.environ['R_TWITTER_CONSUMER_SECRET']]))
    retval.append(''.join(['R_TWITTER_CONSUMER_KEY', '=', os.environ['R_TWITTER_CONSUMER_KEY']]))
    retval.append(''.join(['R_TWITTER_ACCESS_TOKEN', '=', os.environ['R_TWITTER_ACCESS_TOKEN']]))
    retval.append(''.join(['R_TWITTER_ACCESS_TOKEN_SECRET', '=', os.environ['R_TWITTER_ACCESS_TOKEN_SECRET']]))
    retval.append(''.join(['R_REDIS_ENDPOINT', '=', os.environ['R_REDIS_ENDPOINT']]))
    return ';'.join(retval)


if __name__ == "__main__":
    if ARGS.env == 'Prod':
        os.environ['R_DB_HOST'] = os.environ.get('R_PROD_DB_HOST', None)
        os.environ['R_DB_NAME'] = os.environ.get('R_PROD_DB_NAME', None)
        os.environ['R_DB_USERNAME'] = os.environ.get('R_PROD_DB_USERNAME', None)
        os.environ['R_DB_PASSWORD'] = os.environ.get('R_PROD_DB_PASSWORD', None)
        os.environ['R_HOST'] = os.environ.get('R_PROD_HOST', None)
        os.environ['R_HOST_INSTANCE_ID'] = os.environ.get('R_PROD_HOST_INSTANCE_ID', None)
        os.environ['R_TWITTER_CONSUMER_SECRET'] = os.environ.get('R_PROD_TWITTER_CONSUMER_SECRET', None)
        os.environ['R_TWITTER_CONSUMER_KEY'] = os.environ.get('R_PROD_TWITTER_CONSUMER_KEY', None)
        os.environ['R_TWITTER_ACCESS_TOKEN'] = os.environ.get('R_PROD_TWITTER_ACCESS_TOKEN', None)
        os.environ['R_TWITTER_ACCESS_TOKEN_SECRET'] = os.environ.get('R_PROD_TWITTER_ACCESS_TOKEN_SECRET', None)
    elif ARGS.env == 'Test':
        os.environ['R_DB_HOST'] = os.environ.get('R_TEST_DB_HOST', None)
        os.environ['R_DB_NAME'] = os.environ.get('R_TEST_DB_NAME', None)
        os.environ['R_DB_USERNAME'] = os.environ.get('R_TEST_DB_USERNAME', None)
        os.environ['R_DB_PASSWORD'] = os.environ.get('R_TEST_DB_PASSWORD', None)
        os.environ['R_HOST'] = os.environ.get('R_TEST_HOST', None)
        os.environ['R_HOST_INSTANCE_ID'] = os.environ.get('R_TEST_HOST_INSTANCE_ID', None)
        os.environ['R_TWITTER_CONSUMER_SECRET'] = os.environ.get('R_TEST_TWITTER_CONSUMER_SECRET', None)
        os.environ['R_TWITTER_CONSUMER_KEY'] = os.environ.get('R_TEST_TWITTER_CONSUMER_KEY', None)
        os.environ['R_TWITTER_ACCESS_TOKEN'] = os.environ.get('R_TEST_TWITTER_ACCESS_TOKEN', None)
        os.environ['R_TWITTER_ACCESS_TOKEN_SECRET'] = os.environ.get('R_TEST_TWITTER_ACCESS_TOKEN_SECRET', None)
    # In either case, use the client's local redis service
    os.environ['R_REDIS_ENDPOINT'] = '127.0.0.1'

    uwsgi_command = []
    uwsgi_command.append('uwsgi')
    uwsgi_command.append('--socket 127.0.0.1:5000')
    uwsgi_command.append('--protocol=http')
    uwsgi_command.append('--module rheTOracle')
    uwsgi_command.append('--callable app')
    uwsgi_command.append('--master')
    uwsgi_command.append('--processes 1')
    uwsgi_command.append('--threads 2')
    uwsgi_command.append('--env=' + create_uwsgi_env_string())
    print create_uwsgi_env_string()
    os.system(" ".join(uwsgi_command))
