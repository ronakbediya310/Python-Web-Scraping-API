from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)
CORS(app)

@app.route("/api/showreview", methods=['GET'])
def show_review():
    search_item = request.args.get('item', default='', type=str)
    if not search_item:
        return jsonify({'error': 'Item not provided'}), 400
    try:
        website_url = f"https://www.flipkart.com/search?q={search_item}"
        response = requests.get(website_url)
        response.raise_for_status()
        html = BeautifulSoup(response.text, "html.parser")
        product_containers = html.findAll("div", {"class": "_1AtVbE col-12-12"})
        del product_containers[0:3]
        reviews = []
        for product_box in product_containers:
            try:
                product_link = product_box.div.div.div.a['href']
                if product_link:
                    product_link = "https://www.flipkart.com" + product_link
                    product_response = requests.get(product_link)
                    product_response.raise_for_status()
                    product_html = BeautifulSoup(product_response.text, "html.parser")
                    comment_boxes = product_html.find_all('div', {'class': "_16PBlm"})
                    product_name = product_html.find('div', {'class': "aMaAEs"}).div.h1.span.text
                    for comment_box in comment_boxes:
                        try:
                            name = comment_box.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text.strip()
                        except:
                            name = 'No Name'
                        try:
                            rating = comment_box.div.div.div.div.text.strip()
                        except:
                            rating = 'No Rating'
                        try:
                            comment_head = comment_box.div.div.div.p.text.strip()
                        except:
                            comment_head = 'No Comment Heading'
                        try:
                            comment_tag = comment_box.div.div.find_all('div', {'class': ''})
                            cust_comment = comment_tag[0].div.text.strip()
                        except:
                            cust_comment = 'No Comment'
                        review_data = {
                            "Product": product_name,
                            "Name": name,
                            "Rating": rating,
                            "CommentHead": comment_head,
                            "Comment": cust_comment
                        }
                        reviews.append(review_data)

            except Exception as e:
                continue
        return jsonify(reviews), 200, {'Content-Type': 'application/json; charset=utf-8', 'indent': 2}
    except requests.exceptions.HTTPError as err:
        return jsonify({'error': str(err)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host="localhost", port=4500)
