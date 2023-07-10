import json

if __name__ == '__main__':
    with open('101.json') as f:
        a = json.load(f)
        print(a)