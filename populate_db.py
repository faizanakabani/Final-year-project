import os
import json
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL or SUPABASE_KEY not found in environment.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

data = [
  {
    "id": 2,
    "title": "Church of the Holy Spirit",
    "description": "One of Margao's oldest and most magnificent churches built in 1564. Famous for its pristine white Baroque architecture and beautifully decorated altars dedicated to the Virgin Mary.",
    "latitude": 15.2805,
    "longitude": 73.961,
    "imageUrl": None,
    "images": [
      "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRlPPvBzV8e24YgWG4EzWAGf96D-gKKZGb5tg&s",
      "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/06/77/36/ac/caption.jpg?w=900&h=500&s=1"
    ],
    "createdAt": "2026-03-28 07:19:58.00221+00",
    "category": "churches",
    "longDescription": None,
    "shortDescription": None,
    "howTo": None,
    "whatTo": None
  },
  {
    "id": 3,
    "title": "Colva Beach",
    "description": "A legendary stretch of powdery white sands flanked by swaying coconut trees. A buzzing commercial center for sunset lovers, local Goan shacks, and vibrant water sports.",
    "latitude": 15.278019,
    "longitude": 73.912877,
    "imageUrl": "https://chalbanjare.com/crm/sys_images/Colva_Beach1759734932.webp",
    "images": [
      "https://chalbanjare.com/crm/sys_images/Colva_Beach1759734932.webp"
    ],
    "createdAt": "2026-03-28 07:19:58.00221+00",
    "category": "beaches",
    "longDescription": None,
    "shortDescription": None,
    "howTo": None,
    "whatTo": None
  },
  {
    "id": 4,
    "title": "Goa Chitra Museum",
    "description": "An internationally acclaimed ethnography museum located in Benaulim. It houses an organic collection of over 4000 artifacts focusing on Goa's traditional agrarian lifestyle and ancient culture.",
    "latitude": 15.2635,
    "longitude": 73.9317,
    "imageUrl": None,
    "images": [
      "https://s7ap1.scene7.com/is/image/incredibleindia/goa-chitra-museum-goa-1-musthead-hero?qlt=82&ts=1742173887122",
      "https://lh5.googleusercontent.com/proxy/yofLXvgEd1Gen0dRnwbdFRBPlHHRxj8s-ite_IwNSgvrpiPWW2p_9kYOG5YrikCkSytA4FyrZlnPMYI"
    ],
    "createdAt": "2026-03-28 07:19:58.00221+00",
    "category": "museums",
    "longDescription": "Established as a tribute to the eco-friendly and self-sufficient lifestyle of pre-colonial Goans, Goa Chitra is a conglomerate of three distinct museums spread across nearly 1.17 lakh square metres: \r\nGoa Chitra: The flagship museum focusing on Goan ethnography, featuring indigenous tools, pottery, and agrarian implements like a towering five-metre sugarcane grinder.\r\nGoa Chakra: A unique section dedicated to the history of the wheel, showcasing one of India's largest collections of ancient carriages, bullock carts, and palanquins.\r\nGoa Cruti: A collection highlighting Goa’s colonial past under Portuguese rule, displaying the introduction of modern technology and Indo-Portuguese lifestyles. \r\nThe museum has gained international recognition for its conservation efforts, rated by the Archaeological Survey of India as the “topmost contemporary museum” in the country. Beyond its static displays, it serves as a cultural hub, hosting workshops, guest lectures, and concerts to keep traditional art forms alive for younger generations. ",
    "shortDescription": None,
    "howTo": None,
    "whatTo": None
  },
  {
    "id": 9,
    "title": "Chapora Fort",
    "description": "Located at the mouth of the Chapora River, the Chapora Fort is a silent witness to centuries of power struggles between the Portuguese, Marathas, and the Kings of Sawantwadi. The present structure, made of red laterite stone, was completed in 1717 and replaced an earlier 16th-century fortification. Its strategic elevation allowed soldiers to spot enemy ships from miles away. Unlike other Goan forts that have been heavily restored into museums, Chapora retains a rugged, atmospheric charm. Visitors must undertake a short, steep climb to reach the top, where they are rewarded with an unobstructed view of the Arabian Sea and the shifting sands of the northern coastline.\n",
    "latitude": 15.6056,
    "longitude": 73.7336,
    "imageUrl": "https://lh3.googleusercontent.com/gps-cs-s/AHVAweoGaU0vDSWfmF0pdmDtzGymP83NclKS92hb0-Q4X_zbuHBbGmjr5XdlqaSypnohEodeyzDpt47zjrSY7dGWUqHfcvvDU74JH-uhzheyrGK0Z9q4JUv-ykjBatdm0qqOI-z8Ju6L=s680-w680-h510-rw",
    "images": [
      "https://lh3.googleusercontent.com/gps-cs-s/AHVAweoGaU0vDSWfmF0pdmDtzGymP83NclKS92hb0-Q4X_zbuHBbGmjr5XdlqaSypnohEodeyzDpt47zjrSY7dGWUqHfcvvDU74JH-uhzheyrGK0Z9q4JUv-ykjBatdm0qqOI-z8Ju6L=s680-w680-h510-rw"
    ],
    "createdAt": "2026-04-02 15:59:49.815737+00",
    "category": "Fort",
    "longDescription": "Chapora Fort is steeped in a history of shifting power between the Portuguese, the Marathas, and the local Muslim Sultanates. Its location was strategically chosen to monitor the northern borders of the Portuguese \"Old Conquests\" and to prevent inland invasions via the Chapora River. \r\nHistorical Turning Points:\r\nThe Muslim Origin: Long before the Portuguese arrived, a fort known as Shahpura stood here, built by Adil Shah of Bijapur.\r\nPortuguese Rebirth: In 1617, the Portuguese completely rebuilt the structure on the old foundations, naming it the Fort of St. Anthony of Chapora. It featured a church, barracks, and housing for a small garrison.\r\nThe Maratha Threat: The fort was a constant target for the Marathas. In 1684, the Maratha ruler Sambhaji famously captured the fort without a fight after the Portuguese commander surrendered, though it was eventually returned to the Portuguese under a peace treaty. It fell again to the Bhonsles in 1739 before being permanently reclaimed by the Portuguese in 1741. \r\nArchitectural and Cultural Highlights:\r\nDefensive Design: The fort's walls follow the natural contours of the hill, creating an irregular shape. While the internal buildings (like the church and barracks) have vanished, the high outer ramparts and several semicircular bastions remain largely intact.\r\nThe \"Hole in the Wall\": A specific section of the western wall became a pop-culture landmark after being featured in the 2001 Bollywood film Dil Chahta Hai, symbolising friendship and freedom.\r\nThe Viewpoint: From the ramparts, visitors get a 360-degree view: to the south lies the crescent-shaped Vagator Beach, to the north is the vast Morjim Beach, and to the west is the endless expanse of the Arabian Sea.",
    "shortDescription": None,
    "howTo": None,
    "whatTo": None
  },
  {
    "id": 8,
    "title": "Reis Magos Fort",
    "description": "Reis Magos Fort stands at the narrowest point of the Mandovi estuary, making it a strategic \"ambush point\" for defending against enemy ships. Built of reddish laterite stone, the fort is famous for its well-preserved high walls, cylindrical watchtowers, and panoramic views of Panjim. It is closely associated with the nearby Reis Magos Church, the first church built in the Bardez taluka.",
    "latitude": 15.4964,
    "longitude": 73.8091,
    "imageUrl": "https://lh3.googleusercontent.com/gps-cs-s/AHVAweo-8triQY-T8mC7_Pwwv_AsbRvNQq6jgSqfhR2n0UU8QI_CBNbTpuICmWT3ZFZkErRVi-d4s0NmvxLOjZtMronjb25NZ8tK1-8FK7aNaqlYoaMrhlLECEYvVGUilENemzBXCReSig=s680-w680-h510-rw",
    "images": [
      "https://lh3.googleusercontent.com/gps-cs-s/AHVAweo-8triQY-T8mC7_Pwwv_AsbRvNQq6jgSqfhR2n0UU8QI_CBNbTpuICmWT3ZFZkErRVi-d4s0NmvxLOjZtMronjb25NZ8tK1-8FK7aNaqlYoaMrhlLECEYvVGUilENemzBXCReSig=s680-w680-h510-rw"
    ],
    "createdAt": "2026-04-02 15:56:07.660669+00",
    "category": "Fort",
    "longDescription": "Reis Magos Fort holds a unique position in Goan history as a site that evolved from a military outpost into a sophisticated administrative and cultural landmark. Its strategic location at the narrowest point of the Mandovi River allowed its cannons to cross-fire with those of the Gaspar Dias Fort (in Panjim), effectively bottlenecking any enemy fleet attempting to sail toward Old Goa. \r\nHistorical Evolution:\r\nThe Adil Shahi Origin: Before the Portuguese arrival, the site was occupied by an armed outpost of the Adil Shahi Sultanate of Bijapur.\r\nPortuguese Construction: The Portuguese erected the first structure in 1551, significantly expanding it in 1707. It served as a residence for Viceroys and other high-ranking dignitaries arriving from Portugal before they made their official entry into the capital.\r\nMilitary to Prison: Over the centuries, it fended off numerous Maratha attacks. In the early 20th century, its role shifted, and it was used as a prison, notably housing freedom fighters during the Goan Liberation movement.\r\nRestoration: After falling into deep neglect, the fort was restored between 2007 and 2012 through a collaboration between the Helen Hamlyn Trust, the Government of Goa, and the late architect Gerard da Cunha. \r\nArchitectural and Cultural Highlights:\r\nLaterite Grandeur: The fort is constructed from reddish-brown laterite stone and features high sloping walls, classic cylindrical watchtowers (bartizans), and a series of underground rooms and passages.\r\nMario Miranda Gallery: A permanent exhibition of the legendary Goan cartoonist’s work is a major draw, capturing the essence of Goan life through his satirical drawings.\r\nReis Magos Church: Located at the base of the fort, this historic 1555 church is famous for its annual \"Feast of the Three Kings\" and its stunning wood-carved interiors.\r\nPanoramic Vistas: The ramparts offer an unobstructed view across the river to the Panjim skyline, the Mandovi Bridge, and the distant Arabian Sea",
    "shortDescription": None,
    "howTo": None,
    "whatTo": None
  },
  {
    "id": 7,
    "title": "Fort Aguada",
    "description": "Fort Aguada is a majestic 17th-century Portuguese fortress standing at the confluence of the Mandovi River and the Arabian Sea in North Goa. Built in 1612 to protect the coastline from Dutch and Maratha invasions, the fort is renowned for its massive underground freshwater cistern, which once supplied passing ships and gave the site its name, \"Aguada\" (meaning \"water\" in Portuguese). Constructed from local red laterite stone, the complex features a land-side dry moat, high battlements, and a 19th-century lighthouse that is the oldest of its kind in Asia. While its lower portion served as a safe berth for vessels, the upper fort housed the citadel and a notorious high-security prison, which has recently been renovated into a museum dedicated to Goa’s freedom struggle. Today, it remains one of the most well-preserved colonial landmarks in India, offering visitors panoramic coastal views and a deep dive into Goa’s maritime history.\n\n\n",
    "latitude": 15.4925,
    "longitude": 73.7736,
    "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/f/f8/Fort_Aguada_Goa.JPG",
    "images": [
      "https://upload.wikimedia.org/wikipedia/commons/f/f8/Fort_Aguada_Goa.JPG"
    ],
    "createdAt": "2026-04-02 15:31:15.141001+00",
    "category": "Fort",
    "longDescription": "Fort Aguada was the most strategic and prized possession of the Portuguese, designed to encompass the entire peninsula at the southwestern tip of Bardez. Its location at the mouth of the Mandovi River allowed it to control all naval traffic entering the capital of Old Goa. \r\n\r\nHistorical and Architectural Features:\r\nTwo-Tiered Defense: The fort is divided into two segments. The Upper Fort served as a citadel and watering station, housing a massive underground cistern, gunpowder rooms, and a secret escape passage. The Lower Fort provided a safe berth for Portuguese ships and handled direct coastal defense.\r\nAsia’s Oldest Lighthouse: Erected in 1864, the four-story lighthouse once used oil lamps to emit a beacon every seven minutes. While it was decommissioned in 1976, a newer, functioning lighthouse stands nearby which visitors can climb for a small fee.\r\nAguada Central Jail Museum: Repurposed as a prison during the Salazar regime to hold political opponents and freedom fighters, the jail was decommissioned in 2015. In 2021, it was inaugurated as a world-class Interactive Museum that chronicles Goa's 450-year liberation struggle.\r\nMassive Storage: The fort's engineering was a marvel of its time, capable of storing over 2.3 million gallons of fresh water, making it one of the largest freshwater reservoirs in Asia during the 17th century.",
    "shortDescription": None,
    "howTo": None,
    "whatTo": None
  },
  {
    "id": 18,
    "title": "Betul Fort",
    "description": "Betul Fort is a secluded 17th-century coastal bastion in South Goa, commissioned by Chhatrapati Shivaji Maharaj in 1679. Strategically perched where the Sal River meets the Arabian Sea, the fort now consists mostly of atmospheric ruins and a solitary cannon. It is highly regarded by locals and travelers for its panoramic views of Mobor Beach and its quiet, off-the-beaten-path environment.",
    "latitude": 15.1489,
    "longitude": 73.9534,
    "imageUrl": "https://lh3.googleusercontent.com/gps-cs-s/AHVAweozdGfh3Vf8UkmExXGq5yveynxKnyTHtkc0OWXCXTgtljwfWRJFOnO2JGUF85qnMpvisOF40wlYt8FZ09h0L48xEjuyJIao3L4CNsr_zfokLsAR7ukNj0lKGcM7AqMbzQjOYfp3qQ=s680-w680-h510-rw",
    "images": [
      "https://lh3.googleusercontent.com/gps-cs-s/AHVAweozdGfh3Vf8UkmExXGq5yveynxKnyTHtkc0OWXCXTgtljwfWRJFOnO2JGUF85qnMpvisOF40wlYt8FZ09h0L48xEjuyJIao3L4CNsr_zfokLsAR7ukNj0lKGcM7AqMbzQjOYfp3qQ=s680-w680-h510-rw"
    ],
    "createdAt": "2026-04-04 06:02:51.101643+00",
    "category": "Fort",
    "longDescription": "Commissioned during the twilight of the Maratha King’s reign, Betul Fort was a key part of Shivaji Maharaj’s strategy to challenge Portuguese maritime dominance. Unlike the sprawling Portuguese sea forts like Aguada, Betul was a smaller, functional military outpost designed for high visibility and quick defense. Its location allowed the Marathas to control the entry of trade vessels into the Sal River and protect the southern hinterlands of Goa. \r\nArchitecture and Historical Features:\r\nThe Bastion: The most prominent surviving feature is the single, circular bastion perched on the cliffside. It still houses a solitary ancient cannon that overlooks the sea, serving as a silent reminder of the fort's military past.\r\nRuined Ramparts: Most of the fort’s original structure is now in a dilapidated state, with laterite stone walls largely reclaimed by nature. Local historians often refer to it as an \"abandoned archaeological treasure.\"\r\nNatural Vantages: Because of its elevation, the fort provides a 270-degree view. Visitors can see the white sands of Mobor Beach to the north, the winding Sal River to the east, and the vast Arabian Sea to the west.\r\nShivaji Jayanti Celebrations: Every year, local history enthusiasts and devotees of the Maharaj gather here to celebrate his birth anniversary, hoisting the saffron flag to honor its Maratha heritage",
    "shortDescription": None,
    "howTo": None,
    "whatTo": None
  },
  {
    "id": 16,
    "title": "Goa Chitra Museum",
    "description": "An internationally acclaimed ethnography museum located in Benaulim. It houses an organic collection of over 4000 artifacts focusing on Goa's traditional agrarian lifestyle and ancient culture.",
    "latitude": 15.2635,
    "longitude": 73.9317,
    "imageUrl": "https://s7ap1.scene7.com/is/image/incredibleindia/goa-chitra-museum-goa-1-musthead-hero?qlt=82&ts=1742173887122",
    "images": [
      "https://s7ap1.scene7.com/is/image/incredibleindia/goa-chitra-museum-goa-1-musthead-hero?qlt=82&ts=1742173887122",
      "https://lh5.googleusercontent.com/proxy/yofLXvgEd1Gen0dRnwbdFRBPlHHRxj8s-ite_IwNSgvrpiPWW2p_9kYOG5YrikCkSytA4FyrZlnPMYI"
    ],
    "createdAt": "2026-04-04 10:48:07.261019+00",
    "category": "museums",
    "longDescription": "Established as a tribute to the eco-friendly and self-sufficient lifestyle of pre-colonial Goans, Goa Chitra is a conglomerate of three distinct museums spread across nearly 1.17 lakh square metres: \r\nGoa Chitra: The flagship museum focusing on Goan ethnography, featuring indigenous tools, pottery, and agrarian implements like a towering five-metre sugarcane grinder.\r\nGoa Chakra: A unique section dedicated to the history of the wheel, showcasing one of India's largest collections of ancient carriages, bullock carts, and palanquins.\r\nGoa Cruti: A collection highlighting Goas colonial past under Portuguese rule, displaying the introduction of modern technology and Indo-Portuguese lifestyles. \r\n\r\nThe museum has gained international recognition for its conservation efforts, rated by the Archaeological Survey of India as the “topmost contemporary museum” in the country. Beyond its static displays, it serves as a cultural hub, hosting workshops, guest lectures, and concerts to keep traditional art forms alive for younger generations.",
    "shortDescription": None,
    "howTo": None,
    "whatTo": None
  },
  {
    "id": 12,
    "title": "Corjuem Fort",
    "description": "Standing as a sentinel over the riverine trade routes of North Goa, Corjuem Fort is a remarkable example of 18th-century Portuguese military architecture adapted for inland defense. Completed in 1705, the fort’s compact square layout was designed for high efficiency, allowing a small garrison to monitor the river crossings and repel Maratha incursions. Its walls are crafted from dark red laterite stone, featuring ramparts that visitors can still walk upon today for a panoramic view of the island's spice plantations and the Mapusa River. The fort's interior houses a small chapel and barracks, which, while partially in ruins, still evoke the daily life of the soldiers who once guarded this strategic frontier.\n",
    "latitude": 15.5944,
    "longitude": 73.8897,
    "imageUrl": "https://lh3.googleusercontent.com/gps-cs-s/AHVAwercDZd83pJdo3H_P96t5LjdVoI5a-dAJoG30oXc3184ZrXYAsklabMCXZ8Susleoj_qovH436H9kk5VKZoT1z3s1LnMd4tRYOLGxGOwCfoQ83hczPzXDAeOPmFzFSRESawOQqq6=s680-w680-h510-rw",
    "images": [
      "https://lh3.googleusercontent.com/gps-cs-s/AHVAwercDZd83pJdo3H_P96t5LjdVoI5a-dAJoG30oXc3184ZrXYAsklabMCXZ8Susleoj_qovH436H9kk5VKZoT1z3s1LnMd4tRYOLGxGOwCfoQ83hczPzXDAeOPmFzFSRESawOQqq6=s680-w680-h510-rw"
    ],
    "createdAt": "2026-04-02 16:08:33.136044+00",
    "category": "Fort",
    "longDescription": "Corjuem Fort stands as a unique example of Portuguese military architecture adapted for riverine defense. Unlike the massive sea forts along the coast, Corjuem is relatively small but remarkably well-preserved. It was originally built by the Bhonsles of Sawantwadi, but the Portuguese captured it in 1705 under the governorship of Caetano de Melo e Castro. Recognizing its strategic value, they reinforced the structure to guard the \"New Conquests\" and the river passage to the capital. \r\nHistorical and Architectural Highlights:\r\nMilitary School: In the 18th century, the fort served as a prestigious military academy, training soldiers in artillery and defense tactics.\r\nUnique Design: The fort is built in a perfect square with four bastions at each corner. It features high laterite walls with multiple embrasures for cannons and a small chapel dedicated to St. Anthony inside its ramparts.\r\nThe Legend of Ursula e Lancastre: The fort is famously associated with the story of Ursula, an ambitious Portuguese woman who disguised herself as a man to join the military. She served at Corjuem Fort for years before her true identity was discovered after being wounded in battle.\r\nScenic Location: Accessible via a modern suspension bridge from Aldona, the fort offers a 360-degree view of the surrounding lush green islands, the Mapusa River, and the sprawling Goan countryside. ",
    "shortDescription": None,
    "howTo": None,
    "whatTo": None
  },
  {
    "id": 11,
    "title": "Sinquerim Fort",
    "description": "Constructed in 1612, Sinquerim Fort was an integral part of the Portuguese defense network, acting as the primary seaside sentinel for the larger Aguada complex. Its location was chosen for its commanding view of the sea, allowing early detection of enemy vessels attempting to enter the Mandovi River. The fort's most iconic feature is its lower bastion, which pushes out into the waves and often serves as a point for local fishermen and tourists seeking a view of the \"River Princess\" shipwreck in the distance.",
    "latitude": 15.50267,
    "longitude": 73.766925,
    "imageUrl": "https://lh3.googleusercontent.com/gps-cs-s/AHVAweqwPJ7M0ql2tjXjD0gU3yIAN1P3FKWT0yX5pMv0ol3Vatl7hJFgufC93zeLkI8n9dtP6atcL3q5FecE506kkgfZn2MOQLJ0T41yiX0OoPr7Hb_0Z_KuZag8cxbvb7rk3pp2HOQM5MagB6UY=s680-w680-h510-rw",
    "images": [
      "https://lh3.googleusercontent.com/gps-cs-s/AHVAweqwPJ7M0ql2tjXjD0gU3yIAN1P3FKWT0yX5pMv0ol3Vatl7hJFgufC93zeLkI8n9dtP6atcL3q5FecE506kkgfZn2MOQLJ0T41yiX0OoPr7Hb_0Z_KuZag8cxbvb7rk3pp2HOQM5MagB6UY=s680-w680-h510-rw"
    ],
    "createdAt": "2026-04-02 16:05:39.861946+00",
    "category": "Fort",
    "longDescription": "Sinquerim Fort represents a critical piece of Goa’s 17th-century maritime defense system. While often considered a separate entity, it is technically the lower tier of the massive Fort Aguada. The fort was strategically positioned at the mouth of the Mandovi River to protect the entrance to the river and the nearby Portuguese territories from naval attacks. \r\n\r\nHistorical and Strategic Importance:\r\nMaritime Logistics: The fort served as a vital reference point for vessels arriving from Europe. Ships would anchor here to replenish their freshwater supplies from the massive reservoir located in the upper Aguada fort.\r\nDefensive Prowess: Constructed using red laterite stone, the fort features sturdy walls, bastions, and battlements designed to withstand heavy naval bombardment. The upper sections of the Aguada complex once housed 79 cannons and one of Asia’s oldest lighthouses.\r\nPolitical History: During later periods, parts of the Aguada complex (including the nearby prison) were used to hold political prisoners during the Salazar regime and later for drug-related offenses before being abandoned in 1976. ",
    "shortDescription": None,
    "howTo": None,
    "whatTo": None
  },
  {
    "id": 21,
    "title": "Nanuz Fort",
    "description": "Nanuz Fort, also known as Nanus Fort, is a 17th-century Maratha-era stronghold located in the Sattari taluka of North Goa, near Valpoi. Built by Chhatrapati Shivaji Maharaj to guard against Portuguese and Mughal incursions, it later became a significant base for local chieftain Dipaji Rane during the 19th-century Rane Revolts against colonial rule. Today, the fort lies largely in ruins, featuring remnants of 6-foot-high stone walls, a commemorative pillar with an inscription, and panoramic views of the surrounding Mhadei River and lush Western Ghats.",
    "latitude": 15.512,
    "longitude": 74.1349,
    "imageUrl": "https://lh3.googleusercontent.com/gps-cs-s/AHVAweoJVSIlBdgKTddD5cEXX0uQAxGNv5t4VcU5nFViwtFHXgF7htyVlT1cVCe8IUOFpinJaW5h0_5h3uoQw6y2YGOmI-oRjNFrSj6lCDaGJiAFj9Rd8M_9MWs7BHMwTjtjOoi5UOnO30Vw648=s680-w680-h510-rw",
    "images": [
      "https://lh3.googleusercontent.com/gps-cs-s/AHVAweoJVSIlBdgKTddD5cEXX0uQAxGNv5t4VcU5nFViwtFHXgF7htyVlT1cVCe8IUOFpinJaW5h0_5h3uoQw6y2YGOmI-oRjNFrSj6lCDaGJiAFj9Rd8M_9MWs7BHMwTjtjOoi5UOnO30Vw648=s680-w680-h510-rw"
    ],
    "createdAt": "2026-04-04 06:14:42.376385+00",
    "category": "Fort",
    "longDescription": "Nanuz Fort, situated in the Sattari taluka of North Goa near Valpoi, is a historically significant 17th-century fortification that served as a pivotal defensive outpost for the Maratha and Portuguese empires. Originally commissioned by Chhatrapati Shivaji Maharaj, the fort was strategically positioned on a hillock overlooking the Mhadei River to monitor and repel incursions. Its architecture historically reflected a blend of Indo-Portuguese styles, though centuries of conflict between Maratha, Mughal, and Portuguese forces have reduced much of the structure to ruins. \nThe fort's most prominent role in Goan history occurred during the 19th-century Rane Revolts. In 1852, local chieftain Dipaji Rane captured the fort from the Portuguese and transformed it into a strategic military base. From this vantage point, his forces launched guerrilla raids into Portuguese-held territories like Bardez and Tiswadi, successfully evading capture for over three years due to the region's dense, protective forests. Ownership later shifted back to the Portuguese after it was recaptured by soldiers from the Panaji and Quepem barracks.",
    "shortDescription": None,
    "howTo": None,
    "whatTo": None
  },
  {
    "id": 22,
    "title": "Colvale Fort",
    "description": "Colvale Fort, officially the Fortress of São Sebastião, is a 17th-century Portuguese riverine defense work located in North Goa. Built in 1635 and later expanded in 1681, it served as a crucial northern frontier guard for the Bardez taluka against Maratha and Bhonsle incursions. Today, the fort is largely in ruins, offering a quiet, off-the-beaten-path experience with scenic views of the Chapora River and the surrounding lush countryside.\n",
    "latitude": 15.6492,
    "longitude": 73.8342,
    "imageUrl": "https://lh3.googleusercontent.com/gps-cs-s/AHVAweo664G5muKU-FsGbdYrnlEzsk0DGO8cvWTPGTEpP7XQSxRdLlfiLms-PFMEiYZ4SP0Uy9BNMmia9oolDKVJKx_uWfa_AhWy2mOxVAluynY6dpjgVbbDO_8mJdTWk2Sh4OCzUQMu4A=s680-w680-h510-rw",
    "images": [
      "https://lh3.googleusercontent.com/gps-cs-s/AHVAweo664G5muKU-FsGbdYrnlEzsk0DGO8cvWTPGTEpP7XQSxRdLlfiLms-PFMEiYZ4SP0Uy9BNMmia9oolDKVJKx_uWfa_AhWy2mOxVAluynY6dpjgVbbDO_8mJdTWk2Sh4OCzUQMu4A=s680-w680-h510-rw"
    ],
    "createdAt": "2026-04-04 06:18:33.77348+00",
    "category": "Fort",
    "longDescription": "The Colvale Fort, also known as the Fortaleza de São Sebastião de Colvale, stands as a silent witness to the turbulent military history of North Goa. Commissioned in 1635 by the Portuguese Viceroy, Dom Miguel de Noronha (Count of Linhares), its primary purpose was to safeguard the northern boundary of the Bardez province from the growing power of the Bhonsles of Sawantwadi and the Maratha Empire.\nIn 1681, recognizing the fort's strategic vulnerability, the Count of Alvor ordered a significant expansion, transforming it into a more formidable stronghold with thicker walls and reinforced bastions. This expansion was put to the test in 1739 when Maratha forces successfully stormed and captured the fort. However, the Portuguese reclaimed it only two years later in 1741 under the leadership of the Marquis of Louriçal.\n\nArchitectural and Historical Features:\nStrategic Layout: The fort was designed to oversee the Bardez (Chapora) River, controlling boat traffic and preventing surprise inland invasions.\nMilitary Shift: By 1841, the Portuguese military focus shifted, and the regiment stationed at Colvale was moved to Mapusa. Consequently, the fort was abandoned, leading to its gradual decay.\nCultural Blend: Because it was held briefly by the Marathas, the ruins exhibit a fascinating mix of Portuguese military engineering and local stone-working styles.\nCurrent State: While much of the original structure has been reclaimed by nature, visitors can still trace the outlines of the high ramparts and some of the original stone and brickwork. The site is now a peaceful destination, popular for its panoramic riverside views and its proximity to the historic village of Colvale, which was also the home of the famous Goan writer Abbé Faria.\n",
    "shortDescription": None,
    "howTo": None,
    "whatTo": None
  },
  {
    "id": 23,
    "title": "Fernandes Heritage House",
    "description": "The Fernandes Heritage House, also known as Voddlem Ghor (\"Great House\"), is a 500-year-old architectural landmark located in the historic village of Chandor, South Goa. Originally a fortified Hindu house, it evolved into a grand Indo-Portuguese mansion that seamlessly blends traditional Indian design with European colonial flair. Managed by the Fernandes family for generations, it now serves as a private museum showcasing rare antiques, hidden escape routes, and artifacts dating back to the pre-Portuguese era.",
    "latitude": 15.2631,
    "longitude": 74.0478,
    "imageUrl": "https://lh3.googleusercontent.com/gps-cs-s/AHVAweqC8ns3mlhLHZW9NAskqJVApSARg4RT3YbNeRk_Mm9XSB8cmOhICZSjD5k5BWX_Wrq_sIqfs8jRoQt_H2c7S5FNClGMgXXTDUOwiWHpUmSVrlPzPggUkRfdQnIL_m7vkDiU1VLDHA=s680-w680-h510-rw",
    "images": [
      "https://lh3.googleusercontent.com/gps-cs-s/AHVAweqC8ns3mlhLHZW9NAskqJVApSARg4RT3YbNeRk_Mm9XSB8cmOhICZSjD5k5BWX_Wrq_sIqfs8jRoQt_H2c7S5FNClGMgXXTDUOwiWHpUmSVrlPzPggUkRfdQnIL_m7vkDiU1VLDHA=s680-w680-h510-rw"
    ],
    "createdAt": "2026-04-04 06:22:43.524977+00",
    "category": "Heritage",
    "longDescription": "Stepping into the Fernandes Heritage House is often described as walking through a living timeline of Goan history. Located in the Cotta area of Chandor—once the ancient capital of the Kadamba dynasty—this palatial home has roots that pre-date the Portuguese arrival in 1510. \n\nArchitecture and Evolution\nThe house is a masterpiece of cultural fusion. Its core reflects a traditional Hindu design with an inner courtyard, while its facade and 25 rooms feature classic Portuguese elements like ornate balconies, polished wooden floors, and vibrant tiles. \n\nThe Ballroom: A highlight of the mansion, featuring French glass windows, crystal chandeliers, and mirrors that reflect the opulent lifestyle of the affluent Goan nobility.\nUnique Materials: The structure makes extensive use of laterite stone and oyster-shell window panes (instead of glass), which were traditional methods for keeping the interior cool in the tropical heat. \nOneBoard\nOneBoard\n +2\nHistorical Secrets and Defences\nWhat sets this heritage home apart from others in the region are its hidden features designed for protection and escape: \nSecret Passage: A 500-year-old tunnel and basement hideout used by the family during local riots and religious persecutions.\nBullet Marks: The ground floor still bears bullet marks from the 1961 Liberation of Goa, serving as a powerful physical reminder of the region’s transition to Indian independence.\nReligious Heritage: The house preserves images and artifacts from a demolished Shiva temple, on which a local church was later constructed.",
    "shortDescription": None,
    "howTo": None,
    "whatTo": None
  },
  {
    "id": 24,
    "title": "Chhatrapati Shivaji Maharaj Fort छत्रपती शिवाजीचो किल्लो",
    "description": "Originally an Adil Shahi outpost, it was captured and rebuilt by Shivaji Maharaj in 1675. Today, the site features a well-maintained park and a massive, iconic life-size statue of the Maharaj on horseback.",
    "latitude": 15.4128,
    "longitude": 73.9892,
    "imageUrl": "https://lh3.googleusercontent.com/gps-cs-s/AHVAwerCTHdesLVOYN_fCXNhwdk2RkB4bbDmULqzi8p7gmm24_htCsm4el0zeKRe2lD5xiR9dt77CwjYlP3uQRvtcrbHvO7AltTggxaPoDHjQx-LnHZVyKC4B75b3kdkCJE2zm-UgJDM=s680-w680-h510-rw",
    "images": [
      "https://lh3.googleusercontent.com/gps-cs-s/AHVAwerCTHdesLVOYN_fCXNhwdk2RkB4bbDmULqzi8p7gmm24_htCsm4el0zeKRe2lD5xiR9dt77CwjYlP3uQRvtcrbHvO7AltTggxaPoDHjQx-LnHZVyKC4B75b3kdkCJE2zm-UgJDM=s680-w680-h510-rw"
    ],
    "createdAt": "2026-04-04 06:26:32.020721+00",
    "category": "Fort",
    "longDescription": "The fort was a strategic gateway to the Sahyadri mountains. Shivaji first attempted to take it in 1666 but was repelled by the combined forces of the Adil Shahis and Portuguese assistance. He returned in 1675 with a force of 2,000 cavalry and 7,000 infantry, successfully capturing it after a fierce siege. In the late 1970s, the Goa government renovated the area into a public memorial park, making it a major cultural hub where Shivaji Jayanti is celebrated with great fervour.",
    "shortDescription": None,
    "howTo": None,
    "whatTo": None
  },
  {
    "id": 27,
    "title": "Piazza Cross of Assolna Market (Cruzeiro de Assolna)",
    "description": "A towering, vibrant blue-and-white piazza cross situated at the bustling market square in Assolna, Salcete.",
    "latitude": 15.1803516951094,
    "longitude": 73.9713543693112,
    "imageUrl": None,
    "images": [
      "https://kclmxvldjbccfdtnautw.supabase.co/storage/v1/object/public/Simages/Piazza/image%20(3).png",
      "https://kclmxvldjbccfdtnautw.supabase.co/storage/v1/object/public/Simages/Piazza/image%20(4).png"
    ],
    "createdAt": "2026-04-05 05:07:16.645962+00",
    "category": "Piazza Crosses",
    "longDescription": "This monument is the architectural focal point of the Assolna Market. Unlike the more common whitewashed crosses found in many Goan piazzas, this structure is distinguished by its bold blue and white color scheme—a palette often associated with the distinct cultural identity of the Salcete district. The pedestal is remarkably high and multi-tiered, featuring classical masonry elements such as rounded corner columns and scalloped decorative patterns. Historically, Assolna was a strategic military location, once housing a 16th-century fortress. This cross represents the village’s transition from a defensive outpost to a thriving commercial center. It illustrates how religious architecture evolved into civic landmarks, anchoring the social and economic life of the community during village feasts and daily market gatherings.",
    "shortDescription": None,
    "howTo": None,
    "whatTo": None
  }
]

# Filtering out 'images' and other fields that might not be in the 'content' table
# and keeping only what sync_supabase_data uses.
clean_data = []
for item in data:
    clean_item = {
        "title": item.get("title"),
        "description": item.get("description"),
        "longDescription": item.get("longDescription"),
        "howTo": item.get("howTo"),
        "whatTo": item.get("whatTo"),
        "latitude": item.get("latitude"),
        "longitude": item.get("longitude"),
        "imageUrl": item.get("imageUrl"),
        "category": item.get("category"),
        "createdAt": item.get("createdAt")
    }
    clean_data.append(clean_item)

try:
    response = supabase.table('content').insert(clean_data).execute()
    print(f"Successfully inserted {len(clean_data)} items into Supabase 'content' table.")
except Exception as e:
    print(f"Error inserting data: {e}")
