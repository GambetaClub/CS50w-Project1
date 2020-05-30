import requests

def get_value(book_isbn, information):
    res = requests.get("https://www.goodreads.com/book/review_counts.json?&key=ANacHyJRtneWNOKrj1uxg",
                        params={"isbns": book_isbn})
    if res.status_code != 200:
        if res.status_code == 404:
            return render.template("error.html", message="Page not found")
        if res.status_code == 402:
            return render.template("error.html", message="Bad request")
        raise Exception("ERROR: API request unsuccessful.")

    data = res.json()
    for item in data['books']:
        return(item[information])
        
def main():
    information = 'average_rating'
    book_isbn = '1857231082'
    f = get_value(book_isbn,information)
    print(f)

if __name__ == "__main__":
    main()