"""Build the BBB customer-reviews CSV.

BBB (bbb.org) intermittently bot-walls headless browsers, so these 46 reviews
were captured through a real browser session (page text, 5 pages) and are
parsed here into the common schema. Re-running requires re-capturing the text
(BBB blocks scripted fetches); the RAW block below is that captured text.

Published context (real): BBB rating F, 1.09/5 across 46 customer reviews,
212 complaints in last 3 years. BBB is a grievance channel -> essentially all
1-star; treat as an intensity signal, not a balanced sample.
"""
import csv
import os
import re

OUT = os.path.join(os.path.dirname(__file__), "data", "bbb.csv")

RAW = r"""
Review from
Evan K
Date: 07/05/2026
1 star
I have been a loyal WHOOP member for over six years and have recommended the product to countless friends, family members, athletes, and business colleagues. Unfortunately, my experience with their customer support has completely destroyed the trust I had. My account was deleted, resulting in the loss of approximately six years of health, recovery, training, and biometric data. It took nearly two months of repeated emails just to get meaningful responses. After months of frustration, the resolution offered was two free months of service. The hardware and insights may be good when everything works, but a company's true character is revealed when something goes wrong. WHOOP's customer support and account recovery processes fell far short of what customers should expect from a premium subscription service.
Review from
Nws N
Date: 07/03/2026
1 star
I used my CSR credit to buy a whoop in January 2026. The product has been excellent so far. 6 months later they charge my CSR again. I inquired with Whoop and they put the burden of proof that I did not buy anything on me. They cant provide me with an associated order number, email, name, phone number, or any information whatsoever for the near $400 charge on my credit card and refuse to refund it. I had to file fraud. It would appear theyre engaged in fraud and I hope the MA AG investigates.
Review from
Delaney L
Date: 06/16/2026
1 star
Poor usefulness: the app mixes you up with other users and gives wrong information, daily-use metrics are buried, the user guide is not updated, and the return experience feels designed to trap you. Only email returns contact - no humans, no exceptions. When I reached out to customer service, I received only an automated response and could not get meaningful access to a human. The support process did not feel like customer service; it felt like a barrier designed to enforce the policy while avoiding accountability. I regret the purchase and would not recommend WHOOP.
Review from
Aesha J
Date: 04/18/2026
1 star
Buyer Beware! The product itself is basically junk tech that also burned/irritated the skin on my wrist. Stopped wearing because it was basically nonsense, only to discover two years later that Whoop had been charging my card upwards for $230 every year for a subscription that I never signed up for. Whoop never sent subscription renewal emails prior to charging my card, nor did they send receipts. Part of the Whoop business model seems to be sneaky subscription fees charged to device purchasers who have long since thrown that device in the junk drawer.
Review from
Brandy A
Date: 03/16/2026
1 star
I attempted to gift my daughter a 4.0 device, and after trying for over a month to activate her account we gave up. This past weekend, Whoop charged my daughters account $239 for a new 12-month membership. Per their AI-generated email response her account didn't have an active device linked and to access their app she needed to link a device and then cancel her membership through the app. Which is false information, because there is no way to alter your membership details through the app. We have gone to our bank to dispute the charges. I don't want other people to be fraudulently charged for a device/service they never used.
Review from
Viv D
Date: 03/11/2026
1 star
Placed an order with WHOOP on February 26 and my credit card was charged the same day. After nearly three weeks with no shipping updates, I contacted customer support on March 11. Shortly after, I received an email that the company issued a refund without a reason. They stated the order could not be fulfilled. WHOOP held my payment for almost three weeks without notifying me. The refund only occurred after I contacted them.
Review from
Jae C
Date: 03/08/2026
1 star
Whoop refused to honor my return stating that it was marked final sale but when I provided proof that it wasn't, Whoop still refused to refund my purchase. Do NOT give your business to this company.
Review from
James B
Date: 02/28/2026
1 star
Placed an order for a Whoop device and membership as part of a Chase offer. Despite placing my order 5 minutes earlier Whoop states once the order has been placed it cannot be canceled for any reason. They told me I could return the order once delivered for a full refund. So I waited a week, received it, called customer service for a return label (a huge hassle) and I was refunded minus the shipping cost. They forced me to receive it, and then charged me to ship it back. Stupid company, stupid policy, stay far away and just stick with an Apple Watch.
Review from
Chris W
Date: 01/06/2026
1 star
I have been dealing with Whoop, trying to get a replacement for a defective sensor that will no longer pair. After 13 emails going through the same corrective actions and two videos, their recommendation is to tap it harder. I was able to get this connected and working in the first place.
Review from
Gabby O
Date: 12/16/2025
1 star
This company deserves 0 stars. I ordered a WHOOP band and the item was lost in transit with the carrier-it was never delivered. I contacted WHOOP for a resolution. They stated that its not their responsibility once the item is shipped. Any decent company would offer a refund or replacement and file their own claim with the carrier. WHOOP did not offer to help at all.
Review from
Bonnie T
Date: 12/16/2025
1 star
I ordered a replacement sensor after losing my original. Within 24 hours I found my original and contacted the company to cancel prior to dispatch. I was told cancellations were not possible, but I could initiate a return once it arrived. After it arrived I requested a return as instructed. I was then told a return was not possible and the item was final sale. The band does not securely clasp to the sensor device. It frequently falls apart into three pieces. After many emails including videos of the loose connection, they refused to replace the band. Their customer support is not transparent, deceptive. They appear focused on scamming people into their membership.
Review from
shayan s
Date: 11/19/2025
1 star
This company is a scam. they take your money without you knowing.
Review from
Mary M
Date: 10/30/2025
1 star
Do not use this service. Not reputable! I used this service for less than a week. Cancelled (or so I thought) and they keep trying to charge me the $239 yearly fee. I no longer have the item and data shows it was not used after the first week. How can they continue to try to make me pay the fee?
Review from
Justin K
Date: 09/05/2025
1 star
Literally cannot return this through the website or app - scam company, avoid at all costs.
Review from
Nicholas G
Date: 08/08/2025
1 star
They have no customer service to talk to and even when you are charged inappropriately, you will be forced to battle over email for unjustified charges. They say you cancel membership online, but there is no place to do so. These items are sharing personal info with Chinese companies which is never reported. Would stay far away from this company.
Review from
Elaine E
Date: 08/05/2025
1 star
They do not provide customer service when their products and services dont work. No response to email or phone calls. Impossible to get a live person. Results in not receiving the services you have paid for.
Review from
Phillip G
Date: 08/01/2025
1 star
Heart rate data at high heart rates is terrible, tried using the bicep band as recommended and it wasn't any better. I would rather have bad data than no data. The return window is only 30 days so if it takes longer to realize the poor quality of the product you are SOL.
Review from
Garrett B
Date: 07/09/2025
1 star
Very hard to unsubscribe from there account. Makes you do a yearly fee if you want the price to be reasonable and then forces you to go onto a PC to cancel. One of the worst memberships that I have ever subscribed to.
Review from
Zach W
Date: 05/27/2025
1 star
To be fair, the product itself is average. It tracks heart rate, gives rough estimates for calories and steps, and offers vague, gimmicky metrics like Whoop age. What ultimately led me to cancel wasnt the device, but the companys predatory behavior, false promises, and total disregard for long-term customers. I was fully prepared to keep paying for the next 20 years. Rather than waive a $50 upgrade fee they initially promised me, theyd rather lose a loyal customer and buy me out of my membership. That says everything.
Review from
Eoin B
Date: 05/11/2025
1 star
Whoop Band randomly stopped syncing. The support was poor in that the only option offered was to erase all data on the device. I did that and the device still is stuck with delayed syncing. No help from the company.
Review from
Justin P
Date: 03/31/2025
1 star
Decided to try this device to help improve my sleep. 1: the device is useless if you work overnights. 2: the battery packs to charge the device conveniently stop working after your 30 day return period. 3: they fail to mention that if youd like to cancel youll be charged $300+ dollars. 4: most of the data is incorrect unless you spend $500 on accessories. 5: the device is so cheaply constructed that bumping it is enough to break open the clasps and itll fall off your arm. Avoid Whoop like the plague.
Review from
Scott W
Date: 02/28/2025
1 star
I've decided to cancel my Whoop subscription after years of using their fitness band. With 6 months left on my subscription amounting to around $119, they said they will not refund me even though I stopped using their services including app, band, charger, etc.
Review from
Semion S
Date: 11/12/2024
1 star
I accepted the Whoop Free 30 day trial. They charged me $9 to ship me the product and it was defective. I contacted customer support and they were non-responsive for 2 weeks. When someone finally contacted me they would email one sentence every 24 to 48 hrs and then went completely dark. My defective item was never replaced and they wanted another $9 to terminate the trial or they would bill me a full year subscription. I had to close my credit card to avoid these fraudulent charges.
Review from
Scott P
Date: 11/06/2024
1 star
My sensor stopped syncing to the app - I contacted support and received an initial response to reload the app. Now I get a series of errors, from telling me I need new sensor or just not syncing. Support has stopped responding after their initial response. Cannot get anyone from Whoop to support me.
Review from
Sai Sarath K
Date: 10/20/2024
1 star
Whoop is nothing but a scam. Their customer support is terrible. Me and my wife both wanted to do the trial but since we didnt like the devices we returned them. Whoop still charged $250 on my wifes card for annual membership and hasnt refunded it. They charged me $130 for the device and $32 for the first month membership even after returning the device and requesting to cancel. Their practices are predatory.
Review from
Adrian C
Date: 10/07/2024
1 star
Never received their product, and was subsequently charged $330 for a subscription I couldn't take advantage of as I never received their product.
Review from
Tony c
Date: 09/03/2024
1 star
trying to charge me for something i dont have. STAY AWAY.
Review from
Oana D
Date: 06/30/2024
1 star
They are Scammers! If you make the mistake of buying a monthly plan nobody is telling you upfront that if you don't cancel in the first 30 days they will charge you the entire year in monthly installments. This device is totally not worth $360 per year, it is a glorified scam.
Review from
John T
Date: 06/23/2024
1 star
The customer service channel doesnt work. They say they will fix the issue and they dont. Good idea and technology. Good luck if you have any issues.
Review from
Donna F
Date: 06/14/2024
1 star
If there was a zero I would put it! I bought two armbands from them. I paid $250 apiece for a year subscription. I keep getting emails saying that my payment failed and I need to show proof of payment. I have sent them three different emails proving that I paid. They sent me an email saying it was all taken care of. I received two more emails after saying that I still owe them money.
Review from
rob g
Date: 06/07/2024
1 star
Whoop customer service is very slow to reply and mostly canned responses. My daughter bought me a whoop, paying for a year subscription. I transferred the subscription to my name, telling them my daughter would not be using the device. But they kept her account active and tried to bill her annual membership as well. It seems the whole subscription model is designed to create confusion. The device itself is average at best, I never trusted the numbers.
Review from
Chris B
Date: 03/28/2024
1 star
Have had their product for just over 3 months and two days ago it stopped charging, even tried different chargers. 3 attempts with their chatbot and two emails to support no answers back other than 1 automated email. tons of same stories on Whoops own social media from customers and tons more on reddit. Do not buy their products! There is no accountability in servicing your product.
Review from
Angelina K
Date: 03/06/2024
1 star
This tablet is useless it works for a short time then nothing for weeks just spinning/buffering. if it had better data usage i imagine it could be a great product only works where there is wifi no wifi no tablet.
Review from
Jennifer Y
Date: 01/27/2024
1 star
This is really a zero star rating. If you purchase this watch and decide you dont want it, good luck getting your money back. They dont notify you that they received the return, and if you follow up by emailing support, you get canned email replies days later informing you that refunds come 5-7 days after item is received back to Whoop. This is a joke, buyer beware!
Review from
Naydene D
Date: 01/19/2024
1 star
I clicked on a link on my phone and because the information said this was a government funded program I assumed it was legit. In this case it appears to be a scam. After giving all of my personal information I immediately received a text informing me I just need to pay 11 dollars. I never received the tablet although a tracking number and shipping information was provided. I give this company 0 stars and hope someone will investigate them for illegal practices.
Review from
Max B
Date: 01/01/2024
5 stars
I've been a whoop customer since 2019 and always had positive interactions with their support. Overall highly positive experience with them and their products.
Review from
Gregory K
Date: 12/29/2023
1 star
I did my research before even thought of putting in the card. The first red flag was the flimsy envelope. It has a return address of some warehouse that I could not find any information about online. I opened the envelope to find a sim card. No letter, no information or instructions. It is not BBB accredited and definitely doesn't deserve the minimum 1 star.
Review from
John C
Date: 12/19/2023
1 star
Absolutely terrible customer service. I ordered a gift extension as a gift and after about ten emails back and forth Whoop has been unable to assist with how to redeem the order. I have asked for a refund and I still do not have that after 2 weeks of asking and persisting. Its pretty embarrassing that a company cannot even get something this simple correct.
Review from
Melissa M
Date: 12/11/2023
1 star
EXTREMELY upset. Planned to end my contract when it renewed. My card was invalid as it had expired so I didnt worry. They found another place I had made a purchase and used that card and I didnt realize it for months and they will not refund me. Be VERY careful with this. They are extremely difficult to get ahold of and deal with customer service.
Review from
James Gator W
Date: 12/04/2023
1 star
These are the worst providers I've ever had the displeasure of dealing with. I have spent 3 days on and off the phone with them. I applied for one thing then they took my application and turned it into a completely different program that I never wanted. It's been a month since I filed an application and I'm still without any solutions. I will be terminating my services.
Review from
Joel L
Date: 11/22/2023
1 star
Agree with others, inquiries take messaging multiple times dealing with twenty representatives with different names each time misconstruing your concern. Garbage customer service, I think I will need to do a charge back and write off my wasted time with this bad business.
Review from
Richard W
Date: 10/20/2023
1 star
I found whoop doing a search, looked at the website and decided NO. I received a tablet today from them unexpectedly. I never asked for a tablet, never joined any whoop agreement. This is blatant stealing taking advantage of old people.
Review from
Patrick H
Date: 10/02/2023
1 star
There is no monthly membership only 1 year commitment even if you select monthly pay.
Review from
Patrick M
Date: 09/28/2023
1 star
This company is nothing but cyber thugs. Everything went well for the first 6 months and then they just updated me right out of the service. All the while having my money for the subscription for a full year. I figured when the year was up it would just be done. Nope, they charged my card for another full year and have no intentions on refunding me anything.
Review from
Casey M
Date: 08/31/2023
1 star
I loved this piece of tech so much. It gave amazing insight into my sleeping habits and work out routines. However, the billing is udder nonsense. I spent hours on the phone with support trying to cancel, but they lock you into a year contract and that's after buying the hardware. Predatory practice and terrible customer service.
Review from
David M
Date: 08/24/2023
1 star
I recently retired from 20 years in the military. I ordered Whoop because of the hype. It sounded like a great tool. After it broke a few days after arrival, I sent multiple requests asking for a replacement and a restart to the free monthly trial. 4 attempts. Nothing. Today I received an email stating that WHOOP is attempting to charge me almost $300 for a service that I don't have the equipment for and attempted to resolve.
"""


def main():
    rows = []
    blocks = [b.strip() for b in RAW.split("Review from") if b.strip()]
    for b in blocks:
        lines = [ln.strip() for ln in b.split("\n") if ln.strip()]
        author = lines[0]
        date = next((ln.replace("Date:", "").strip() for ln in lines
                     if ln.startswith("Date:")), "")
        m = next((re.match(r"(\d+)\s+stars?$", ln) for ln in lines
                  if re.match(r"\d+\s+stars?$", ln)), None)
        rating = m.group(1) if m else ""
        # text = everything after the "N star(s)" line
        idx = next(i for i, ln in enumerate(lines) if re.match(r"\d+\s+stars?$", ln))
        text = " ".join(lines[idx + 1:])
        rows.append({
            "source": "bbb",
            "id": f"{author}|{date}",
            "rating": rating,
            "date": date,
            "author": author,
            "title": "",
            "text": text,
            "version": "",
        })

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["source", "id", "rating", "date",
                                          "author", "title", "text", "version"])
        w.writeheader()
        w.writerows(rows)
    print(f"[bbb] wrote {len(rows)} reviews -> {OUT}")


if __name__ == "__main__":
    main()
