import argparse

from get_drunk_telegram_bot.bot.server import create_server


def parse_server_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default='8888')
    parser.add_argument('--token', type=str, required=True)
    parser.add_argument('--web-hook-url', type=str, required=True)
    parser.add_argument('--debug', action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_server_args()
    if args.debug:
        print("Creating server...")
    app = create_server(args)

    # use_reloader is false due to problems with CUDA and multiprocessing
    app.run(port=args.port, debug=args.debug, use_reloader=False)
