import json

if __name__ == '__main__':
    with open('reports/4.json') as f:
        a = json.load(f)
        print(a)