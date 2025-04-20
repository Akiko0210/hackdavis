import json
import requests
from bs4 import BeautifulSoup
import re

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; WebScraper/1.0)"
}

hackathon_data = {
    "hackathons": []
}

def fetch_hackathon_data(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    # Remove the built-with section entirely
    built_with = soup.find(id="built-with")
    if built_with:
        built_with.decompose()

    # Title
    og_title_tag = soup.find("meta", attrs={"property": "og:title"})
    og_title = og_title_tag['content'] if og_title_tag else "No Title"

    og_desc_tag = soup.find("meta", attrs={"property": "og:description"})
    og_desc = og_desc_tag['content'] if og_desc_tag else "No Description"

    app_details = soup.find(id="app-details-left")
    story = ""
    github = ""

    if app_details:
        divs = app_details.find_all("div", recursive=False)
        
        if len(divs) >= 2:
            info_div = divs[1]

            for i in info_div:

                if i.name == "h2":
                    story = story + i.get_text(strip=True) + ": "

                if i.name == "p":
                    story += i.get_text(strip=True)

                if i.name == "ul":
                    story = story + i.get_text(strip=True) + ","

        for a in app_details.find_all("a", href=True):
            href = a['href']
            if "https://github.com/" in href:
                github = href
    
    return {
        "title": og_title,
        "description": og_desc,
        "story": story.strip(),
        "github": github,
        "url": url
    }

def fetch_project_links(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        
        if "There are no submissions which match your criteria." in soup.text:
            return 404

        anchors = soup.find_all("a", href=True)
        project_data = []

        for a in anchors:
            if re.match(r"^https://devpost\.com/software/", a["href"]):
                project_data.append(fetch_hackathon_data(a["href"]))
        
        return project_data

if __name__ == "__main__":
    with open('data.json', 'r') as file:
        data = json.load(file)
    
    i = 1
    for hackathon in data["hackathons"]:
        projects = []

        while True:
            return_data = fetch_project_links(hackathon["url"] + "project-gallery" + "?page=" + str(i))
            
            if return_data == 404 or return_data == []:
                i = 1
                break
            
            projects.append(return_data)
            i += 1
        
        sample = {
            "title": hackathon["title"],
            "location": hackathon["displayed_location"]["location"],
            "url": hackathon["url"],
            "submission_dates": hackathon["submission_period_dates"],
            "themes": [theme["name"] for theme in hackathon["themes"]],
            "organization": hackathon["organization_name"],
            "winners": hackathon["winners_announced"],
            "projects": projects,
        }
        
        hackathon_data['hackathons'].append(sample)

with open("hackathon_data.json", "w") as json_file:
    json.dump(hackathon_data, json_file, indent=4)