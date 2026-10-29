import json

from trading_strategy import build_dashboard_data


def main():
    data = build_dashboard_data()
    with open('dashboard_data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, default=str, allow_nan=False)
    print('dashboard_data.json created successfully.')


if __name__ == '__main__':
    main()
