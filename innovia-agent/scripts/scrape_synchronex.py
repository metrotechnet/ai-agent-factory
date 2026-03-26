from playwright.sync_api import sync_playwright
import json
import time

def scrape():


    results = []
    print("[INFO] Lancement de Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("[INFO] Accès à la page des centres...")
        page.goto("https://reseaucctt.ca/centres")
        page.wait_for_timeout(3000)

        links = page.query_selector_all("a")
        print(f"[DEBUG] Nombre de liens trouvés : {len(links)}")

        urls = []
        for l in links:
            href = l.get_attribute("href")
            if href and ("/centers/" in href or "/centres/" in href):
                urls.append(href)

        urls = list(set(urls))
        print(f"[DEBUG] Nombre d'URLs de centres trouvées : {len(urls)}")
        #Clear json file if exists
        with open("cctt_dataset.json", "w", encoding="utf-8") as f:
            json.dump([], f)

        for url in urls:
            if not url.startswith("http"):
                url = "https://reseaucctt.ca" + url

            print(f"[INFO] Scraping {url}")
            page.goto(url)
            page.wait_for_timeout(2000)


            # HERO SECTION (adapté à la structure fournie)
            name = page.query_selector(".hero__title")
            nom_val = name.inner_text() if name else None
            subtitle = page.query_selector(".hero__subtitle")
            subtitle_val = subtitle.inner_text() if subtitle else None
            establishment = page.query_selector(".hero__establishment")
            establishment_val = establishment.inner_text() if establishment else None



            # Extraction de la description (plusieurs paragraphes possibles)
            description = []
            desc_paragraphs = page.query_selector_all(".center__presentation p")
            if desc_paragraphs:
                for p in desc_paragraphs:
                    description.append(p.inner_text())
                 
            # Secteurs d'activités
            secteurs = []
            secteurs_links = page.query_selector_all(".sectors__buttons a")
            for a in secteurs_links:
                secteurs.append(a.inner_text())
            # Expertises
            expertises = []
            expertises_badges = page.query_selector_all(".center__tags .badge")
            for badge in expertises_badges:
                expertises.append(badge.inner_text())
            # Exemples d'application
            exemples = []
            exemples_items = page.query_selector_all("#collapseApplication .features-list li")
            for li in exemples_items:
                exemples.append(li.inner_text())
            # Équipements
            equipements = []
            equip_items = page.query_selector_all("#collapseEquipements .features-list li")
            for li in equip_items:
                equipements.append(li.inner_text())


            # CARD-INFO (adapté à la structure fournie)
            logo = None
            website = None
            card_logo_a = page.query_selector(".contact__logo")
            if card_logo_a:
                logo = card_logo_a.get_attribute("src")
                parent_a = card_logo_a.evaluate_handle('node => node.closest("a")')
                if parent_a:
                    website = parent_a.evaluate('el => el ? el.getAttribute("href") : null')

            # Contact information (dans .contact__information li)
            contact_information = []
            contact_info_items = page.query_selector_all(".contact__information li")
            for li in contact_info_items:
                contact_information.append(li.inner_text())

            # Contact-list (dans .contact-list li)
            contact_list = []
            contact_list_items = page.query_selector_all(".contact-list li")
            for li in contact_list_items:
                contact_list.append(li.inner_text())

            # contact__cegep (logo du cégep)
            cegep_logo = None
            cegep_img = page.query_selector(".contact__cegep img")
            if cegep_img:
                cegep_logo = cegep_img.get_attribute("src")


            # Médias (images)
            medias = []
            imgs = page.query_selector_all("img")
            for img in imgs:
                src = img.get_attribute('src')
                if src and '/medias/' in src:
                    medias.append(src)


            results.append({
                "url": url,
                "nom": nom_val,
                "subtitle": subtitle_val,
                "establishment": establishment_val,
                "website": website,
                "description": description,
                "secteurs": secteurs,
                "expertises": expertises,
                "exemples": exemples,
                "equipements": equipements,
                "logo": logo,
                "contact_information": contact_information,
                "contact_list": contact_list,
                "cegep_logo": cegep_logo,
                "medias": medias
            })

            # Sauvegarde incrémentale après chaque centre
            with open("cctt_dataset.json", "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"[INFO] Progression sauvegardée ({len(results)} centres)")

        browser.close()

if __name__ == "__main__":
    scrape()