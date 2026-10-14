try:
    import errors
    import requests
except Exception as e:
    print(e)

def get_quote():

    try:
        res = requests.get("https://dummyjson.com/quotes/random")
        data = res.json()
        print(data)
    except:
        errors.error("Could not receive quote (Are you connected to the internet?)")
        data = {"quote" : "Could not receive quote (Are you connected to the internet?)",
                "author" : "",}
    return data