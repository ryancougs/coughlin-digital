"""Coughlin Digital demo generator.
python3 build.py [slug ...]  -> writes ../site/demo/<slug>/ (index.html, img/, qr.png)
"""
import json, os, shutil, sys
from jinja2 import Environment, FileSystemLoader
from PIL import Image
import segno

HERE = os.path.dirname(os.path.abspath(__file__))
STOCK = os.path.join(HERE, '..', 'stock')
OUT = os.path.join(HERE, '..', 'site', 'demo')

def T(fr, en=None):
    return {'fr': fr, 'en': en if en is not None else fr}

DAYS = [('Dimanche', 'Sunday'), ('Lundi', 'Monday'), ('Mardi', 'Tuesday'), ('Mercredi', 'Wednesday'),
        ('Jeudi', 'Thursday'), ('Vendredi', 'Friday'), ('Samedi', 'Saturday')]

def fr_t(m):
    h, mm = divmod(m, 60)
    return f"{h}\u00a0h\u00a0{mm:02d}" if mm else f"{h}\u00a0h"

def en_t(m):
    h, mm = divmod(m, 60)
    ap = 'a.m.' if h < 12 else 'p.m.'
    h12 = h % 12 or 12
    return f"{h12}:{mm:02d} {ap}" if mm else f"{h12} {ap}"

def hours(spec):
    """spec: dict day_index(0=Sun) -> (start_min, end_min) or None. Groups consecutive equal days (Mon-first order)."""
    order = [1, 2, 3, 4, 5, 6, 0]
    rows, i = [], 0
    while i < len(order):
        d = order[i]; v = spec.get(d); j = i
        while j + 1 < len(order) and spec.get(order[j + 1]) == v:
            j += 1
        ds = order[i:j + 1]
        if len(ds) == 1:
            lab = T(DAYS[ds[0]][0], DAYS[ds[0]][1])
        else:
            lab = T(f"{DAYS[ds[0]][0]} au {DAYS[ds[-1]][0].lower()}", f"{DAYS[ds[0]][1]} to {DAYS[ds[-1]][1]}")
        if v is None:
            tm = T('Fermé', 'Closed')
        elif v == (0, 1440):
            tm = T('24 h sur 24', 'Open 24 hours')
        else:
            tm = T(f"{fr_t(v[0])} à {fr_t(v[1])}", f"{en_t(v[0])} to {en_t(v[1])}")
        rows.append({'d': ','.join(map(str, ds)), 'label': lab, 'time': tm})
        i = j + 1
    js = json.dumps([list(spec[d]) if spec.get(d) else None for d in range(7)])
    return rows, js

H = lambda h, m=0: h * 60 + m

FONTS = {
    'cormorant': ('family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500;1,600&family=Manrope:wght@400;500;600;700', "'Cormorant Garamond', Georgia, serif", "'Manrope', system-ui, sans-serif"),
    'fraunces': ('family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;1,9..144,500&family=Inter:wght@400;500;600;700', "'Fraunces', Georgia, serif", "'Inter', system-ui, sans-serif"),
    'dmserif': ('family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@400;500;600;700', "'DM Serif Display', Georgia, serif", "'DM Sans', system-ui, sans-serif"),
    'grotesk': ('family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700', "'Space Grotesk', system-ui, sans-serif", "'Inter', system-ui, sans-serif"),
    'playfair': ('family=Playfair+Display:ital,wght@0,500;0,600;1,500&family=Jost:wght@400;500;600', "'Playfair Display', Georgia, serif", "'Jost', system-ui, sans-serif"),
    'barlow': ('family=Barlow+Condensed:wght@600;700&family=Barlow:wght@400;500;600;700', "'Barlow Condensed', Impact, sans-serif", "'Barlow', system-ui, sans-serif"),
}

def theme(font, **kw):
    q, disp, body = FONTS[font]
    kw.update(display=disp, body=body)
    return q, kw

# ---------------------------------------------------------------- businesses
B = {}

# ---- Pâtisserie Marian ---------------------------------------------------
fq, th = theme('cormorant', bg='#f6efe4', surface='#fffaf3', text='#2a1d14', muted='#7a6656', accent='#a8692a',
               accent_ink='#ffffff', line='rgba(42,29,20,.13)', display_weight=600, display_tracking='-0.01em', hero_em='#ffd9a0')
rows, js = hours({1: (H(10), H(19)), 2: (H(10), H(19)), 3: (H(10), H(19)), 4: (H(10), H(19)), 5: (H(10), H(19)), 6: (H(10), H(18)), 0: (H(10), H(18))})
B['patisserie-marian'] = dict(
    name='Pâtisserie Marian', initials='M', fonts=fq, theme=th, tagline_plain='Pâtisserie égyptienne · Pierrefonds',
    kind=T('Pâtisserie égyptienne', 'Egyptian pastry shop'),
    phone='438-801-8026', phone_tel='+14388018026', rating='5.0', reviews=93, city='Pierrefonds, QC',
    address='4871, boul. Saint-Charles<br>Pierrefonds, QC H9H 3E4', address_q='4871 Boulevard Saint-Charles, Pierrefonds, QC H9H 3E4',
    maps_q='Pâtisserie Marian 4871 Boulevard Saint-Charles',
    nav=[{'href': '#choose', 'label': T('Commander', 'Order')}, {'href': '#gallery', 'label': T('Nos douceurs', 'Our sweets')}, {'href': '#visit', 'label': T('Nous trouver', 'Visit')}],
    hero=dict(img='hero.jpg', src='sw17', pos='center',
              eyebrow=T('Pâtisserie familiale · Pierrefonds', 'Family pastry shop · Pierrefonds'),
              title={'fr': ['Le goût', "de l’<em>Égypte</em>,", 'à deux pas.'], 'en': ['The taste', 'of <em>Egypt</em>,', 'around the corner.']},
              lead=T('Kunafa, basbousa et baklava faits avec soin, comme là-bas. Appelez d’avance pour réserver votre sélection.',
                     'Kunafa, basbousa and baklava made with care, just like back home. Call ahead to reserve your selection.'),
              cta=T('Réserver ma sélection', 'Reserve my selection'), cta_href='#choose',
              meta=[{'big': T('7 jours', '7 days'), 'small': T('ouvert toute la semaine', 'open all week')},
                    {'big': T('Familiale', 'Family'), 'small': T('entreprise de quartier', 'owned and run')}]),
    marquee=[T('Kunafa'), T('Basbousa'), T('Baklava'), T('Plateaux pour fêtes', 'Party trays'), T('Commandes par téléphone', 'Phone orders')],
    picker=dict(eyebrow=T('Commander', 'Order'), title=T('C’est pour quelle occasion?', 'What’s the occasion?'),
                sub=T('Choisissez, puis envoyez-nous un texto. On prépare tout pour votre arrivée.', 'Pick one, then send us a text. We’ll have it ready when you arrive.'),
                cta=T('Envoyer un texto', 'Send a text'),
                options=[
                    dict(icon='🎉', img='p1.jpg', src='sw11', title=T('Une fête', 'A party'), desc=T('Anniversaire, mariage, Aïd', 'Birthday, wedding, Eid'),
                         panel_title=T('Un plateau qui disparaît en un clin d’œil', 'A tray that disappears in minutes'),
                         panel_text=T('Dites-nous le nombre d’invités et la date. On compose un assortiment sur mesure.', 'Tell us how many guests and the date. We’ll put together a custom assortment.'),
                         sms=T('Bonjour, j’aimerais commander un plateau pour une fête. Nombre d’invités: __  Date: __', 'Hi, I’d like to order a party tray. Number of guests: __  Date: __')),
                    dict(icon='🫖', img='p2.jpg', src='sw12', title=T('Une visite', 'A visit'), desc=T('Une boîte à offrir', 'A box to bring along'),
                         panel_title=T('Une boîte à offrir', 'A box to bring along'),
                         panel_text=T('Le cadeau parfait quand on est reçu chez quelqu’un.', 'The perfect gift when you’re visiting family or friends.'),
                         sms=T('Bonjour, j’aimerais réserver une boîte de pâtisseries pour __ (date).', 'Hi, I’d like to reserve a box of pastries for __ (date).')),
                    dict(icon='🍯', img='p3.jpg', src='sw5', title=T('Pour moi', 'Just for me'), desc=T('La sélection du jour', 'Today’s selection'),
                         panel_title=T('Kunafa, basbousa, baklava', 'Kunafa, basbousa, baklava'),
                         panel_text=T('Passez nous voir. Il y a souvent quelque chose de nouveau à goûter.', 'Drop by. There’s often something new to try.'),
                         sms=T('Bonjour, qu’avez-vous aujourd’hui? J’aimerais passer vers __ h.', 'Hi, what do you have today? I’d like to stop by around __.')),
                    dict(icon='✨', img='p4.jpg', src='sw15', title=T('Commande spéciale', 'Special order'), desc=T('Une grande kunafa, un format précis', 'A large kunafa, a specific size'),
                         panel_title=T('Une demande précise?', 'Something specific in mind?'),
                         panel_text=T('Écrivez-nous ce que vous cherchez. On vous répond avec ce qui est possible.', 'Tell us what you’re looking for and we’ll tell you what we can do.'),
                         sms=T('Bonjour, j’ai une commande spéciale: __', 'Hi, I have a special order: __')),
                ]),
    split=dict(img='split.jpg', src='sw14', eyebrow=T('Notre maison', 'Our house'), title=T('Fait avec soin, comme là-bas.', 'Made with care, like back home.'),
               intro=T('Une pâtisserie familiale où chaque bouchée goûte l’Égypte. Nos clients le disent mieux que nous.', 'A family pastry shop where every bite tastes like Egypt. Our customers say it best.'),
               features=[dict(title=T('Le vrai goût égyptien', 'Real Egyptian flavour'), text=T('Des recettes traditionnelles, des pâtisseries fraîches.', 'Traditional recipes, fresh pastries.')),
                         dict(title=T('Une sélection sur mesure', 'A selection made for you'), text=T('On compose votre boîte selon vos goûts.', 'We put your box together the way you like it.')),
                         dict(title=T('Des prix raisonnables', 'Reasonable prices'), text=T('Pour se faire plaisir sans y penser deux fois.', 'A treat you don’t have to think twice about.')),
                         dict(title=T('Stationnement gratuit', 'Free parking'), text=T('Juste devant, dans le centre commercial.', 'Right out front, in the strip mall.'))]),
    gallery_head=dict(eyebrow=T('Nos douceurs', 'Our sweets'), title=T('À commander, à offrir, à savourer.', 'To order, to share, to savour.'),
                      sub=T('Photos d’exemple. Vos vraies photos les remplaceront.', 'Sample photos. Your real photos will replace them.')),
    gallery=[dict(img='g1.jpg', src='sw17', cap=T('Baklava')), dict(img='g2.jpg', src='sw5', cap=T('Kunafa')), dict(img='g3.jpg', src='sw3', cap=T('Assortiment', 'Assortment')),
             dict(img='g4.jpg', src='sw12', cap=T('Avec le thé', 'With tea')), dict(img='g5.jpg', src='sw15', cap=T('Kunafa ronde', 'Round kunafa'))],
    review_block=dict(title=T('93 avis. Que des 5 étoiles.', '93 reviews. All five stars.'),
                      text=T('Ce qui revient le plus souvent dans les avis de nos clients:', 'What comes up most in our customers’ reviews:'),
                      themes=[T('Authentique', 'Authentic'), T('Toujours frais', 'Always fresh'), T('Accueil chaleureux', 'Warm welcome'), T('Prix raisonnables', 'Reasonable prices')]),
    visit_title=T('Passez nous voir.', 'Come say hello.'), hours=rows, hours_js=js,
    cta=dict(img='cta.jpg', src='sw16', title=T('Une fête qui s’en vient?', 'Party coming up?'), btn=T('Appeler pour commander', 'Call to order')),
)

# ---- Pâtisserie Halwanji -------------------------------------------------
fq, th = theme('fraunces', bg='#0f1913', surface='#15221a', text='#f3ecdd', muted='#a9b5a8', accent='#e3a83f',
               accent_ink='#1a1306', line='rgba(243,236,221,.12)', display_weight=600, display_tracking='-0.02em')
rows, js = hours({1: (H(10), H(16)), 2: (H(10), H(16)), 3: (H(8, 30), H(19)), 4: (H(8, 30), H(19)), 5: (H(8, 30), H(19)), 6: (H(8), H(19)), 0: (H(8), H(19))})
B['patisserie-halwanji'] = dict(
    name='Halwanji', initials='H', fonts=fq, theme=th, tagline_plain='Cuisine et pâtisseries · Roxboro',
    kind=T('Cuisine et pâtisseries', 'Kitchen & pastries'),
    phone='514-464-8866', phone_tel='+15144648866', rating='4.8', reviews=278, city='Roxboro, QC',
    address='11503, boul. Gouin Ouest<br>Roxboro, QC H8Y 1Y1', address_q='11503 Boulevard Gouin Ouest, Roxboro, QC H8Y 1Y1',
    maps_q='Pâtisserie Halwanji 11503 Boulevard Gouin Ouest',
    nav=[{'href': '#choose', 'label': T('Commander', 'Order')}, {'href': '#gallery', 'label': T('Le menu', 'The menu')}, {'href': '#visit', 'label': T('Nous trouver', 'Visit')}],
    hero=dict(img='hero.jpg', src='me4', pos='center',
              eyebrow=T('Roxboro · Ouest-de-l’Île', 'Roxboro · West Island'),
              title={'fr': ['Des repas', 'généreux.', 'Des desserts <em>frais</em>.'], 'en': ['Generous', 'meals.', '<em>Fresh</em> desserts.']},
              lead=T('Kebbé, kabsa, jarrets d’agneau et falafel, puis knafeh, gâteaux et baklava. Tout est frais, et les portions sont généreuses.',
                     'Kibbeh, kabsa, lamb shanks and falafel, then knafeh, cakes and baklava. Everything is fresh, and the portions are generous.'),
              cta=T('Commander', 'Order now'), cta_href='#choose',
              meta=[{'big': T('Repas + desserts', 'Meals + desserts'), 'small': T('au même endroit', 'under one roof')},
                    {'big': T('7 jours', '7 days'), 'small': T('ouvert toute la semaine', 'open all week')}]),
    marquee=[T('Knafeh'), T('Kebbé', 'Kibbeh'), T('Kabsa'), T('Baklava'), T('Gâteaux', 'Cakes'), T('Falafel'), T('Foul')],
    picker=dict(eyebrow=T('Commander', 'Order'), title=T('Qu’est-ce qui vous ferait plaisir?', 'What are you craving?'),
                sub=T('Choisissez, envoyez un texto, passez prendre votre commande.', 'Pick one, send a text, pick up your order.'),
                cta=T('Envoyer un texto', 'Send a text'),
                options=[
                    dict(icon='🍽️', img='p1.jpg', src='me3', title=T('Un repas', 'A meal'), desc=T('Kabsa, jarrets d’agneau, kebbé', 'Kabsa, lamb shanks, kibbeh'),
                         panel_title=T('Un vrai repas, pas une collation', 'A real meal, not a snack'),
                         panel_text=T('Les portions sont généreuses. Commandez d’avance et passez prendre.', 'The portions are generous. Order ahead and pick it up.'),
                         sms=T('Bonjour, j’aimerais commander pour emporter: __  Heure: __', 'Hi, I’d like to order for pickup: __  Time: __')),
                    dict(icon='👨‍👩‍👧', img='p2.jpg', src='me4', title=T('Pour la famille', 'For the family'), desc=T('Un plateau pour tout le monde', 'A spread for everyone'),
                         panel_title=T('De quoi nourrir toute la tablée', 'Enough for the whole table'),
                         panel_text=T('Dites-nous combien vous êtes. On vous propose un assortiment.', 'Tell us how many people. We’ll suggest a spread.'),
                         sms=T('Bonjour, j’aimerais commander pour __ personnes, pour le __ (date).', 'Hi, I’d like to order for __ people, on __ (date).')),
                    dict(icon='🎂', img='p3.jpg', src='sw10', title=T('Un gâteau', 'A cake'), desc=T('Fait avec de bons ingrédients', 'Made with top ingredients'),
                         panel_title=T('Un gâteau pour l’occasion', 'A cake for the occasion'),
                         panel_text=T('Anniversaire ou fête? Écrivez-nous la date et le nombre de personnes.', 'Birthday or celebration? Text us the date and how many people.'),
                         sms=T('Bonjour, j’aimerais commander un gâteau pour __ personnes, le __ (date).', 'Hi, I’d like to order a cake for __ people, on __ (date).')),
                    dict(icon='🍯', img='p4.jpg', src='sw2', title=T('Des desserts', 'Desserts'), desc=T('Knafeh, baklava', 'Knafeh, baklava'),
                         panel_title=T('Knafeh et baklava, tout frais', 'Knafeh and baklava, fresh'),
                         panel_text=T('Moelleux, frais, comme on les aime. Pour vous ou à offrir.', 'Soft, fresh, just right. For you or to share.'),
                         sms=T('Bonjour, j’aimerais réserver des desserts: __', 'Hi, I’d like to reserve some desserts: __')),
                ]),
    split=dict(img='split.jpg', src='me2', eyebrow=T('Chez Halwanji', 'At Halwanji'), title=T('Fait frais, servi avec le sourire.', 'Made fresh, served with a smile.'),
               intro=T('Une adresse de quartier que nos clients appellent leur « trésor caché » de l’Ouest-de-l’Île.', 'A neighbourhood spot our customers call a hidden gem of the West Island.'),
               features=[dict(title=T('Tout est frais', 'Everything is fresh'), text=T('Des repas et des desserts préparés avec de bons ingrédients.', 'Meals and desserts made with good ingredients.')),
                         dict(title=T('Des portions généreuses', 'Generous portions'), text=T('Un plat, et vous êtes servi pour le repas.', 'One plate and you’re set for the meal.')),
                         dict(title=T('Un accueil chaleureux', 'A warm welcome'), text=T('Une équipe sympathique, un endroit propre.', 'A friendly team in a clean space.'))]),
    gallery_head=dict(eyebrow=T('Le menu', 'The menu'), title=T('Du salé au sucré.', 'From savoury to sweet.'),
                      sub=T('Photos d’exemple. Vos vraies photos les remplaceront.', 'Sample photos. Your real photos will replace them.')),
    gallery=[dict(img='g1.jpg', src='me1', cap=T('Mezzés', 'Mezze')), dict(img='g2.jpg', src='sw2', cap=T('Baklava')), dict(img='g3.jpg', src='me6', cap=T('Salades fraîches', 'Fresh salads')),
             dict(img='g4.jpg', src='sw10', cap=T('Pâtisseries', 'Pastries')), dict(img='g5.jpg', src='me3', cap=T('Plats chauds', 'Hot dishes'))],
    review_block=dict(title=T('278 avis. 4,8 étoiles.', '278 reviews. 4.8 stars.'),
                      text=T('Ce qui revient le plus souvent dans les avis de nos clients:', 'What comes up most in our customers’ reviews:'),
                      themes=[T('Frais', 'Fresh'), T('Portions généreuses', 'Huge portions'), T('Knafeh et baklava', 'Knafeh and baklava'), T('Accueil chaleureux', 'Warm service')]),
    visit_title=T('Passez nous voir.', 'Come by.'), hours=rows, hours_js=js,
    cta=dict(img='cta.jpg', src='me5', title=T('Une grande tablée ce week-end?', 'Feeding a crowd this weekend?'), btn=T('Appeler pour commander', 'Call to order')),
)

# ---- Boulangerie & Pâtisserie Parfait ------------------------------------
fq, th = theme('dmserif', bg='#fbf6f1', surface='#ffffff', text='#2b2022', muted='#7d6c6c', accent='#6f8f2f',
               accent_ink='#ffffff', line='rgba(43,32,34,.12)', display_weight=400, display_tracking='-0.01em', hero_em='#cfe39a')
rows, js = hours({d: (H(10), H(21)) for d in range(7)})
B['patisserie-parfait'] = dict(
    name='Pâtisserie Parfait', initials='P', fonts=fq, theme=th, tagline_plain='Boulangerie et pâtisserie · Pierrefonds',
    kind=T('Boulangerie et pâtisserie', 'Bakery & pastry shop'),
    phone='514-620-7000', phone_tel='+15146207000', rating='4.5', reviews=77, city='Pierrefonds, QC',
    address='15779, boul. de Pierrefonds<br>Pierrefonds, QC H9H 3X6', address_q='15779 Boulevard de Pierrefonds, Pierrefonds, QC H9H 3X6',
    maps_q='Boulangerie Patisserie Parfait 15779 Boulevard de Pierrefonds',
    nav=[{'href': '#choose', 'label': T('Commander', 'Order')}, {'href': '#gallery', 'label': T('Nos douceurs', 'Our sweets')}, {'href': '#visit', 'label': T('Nous trouver', 'Visit')}],
    hero=dict(img='hero.jpg', src='sw1', pos='center 60%',
              eyebrow=T('Pierrefonds · ouvert 7 jours', 'Pierrefonds · open 7 days'),
              title={'fr': ['Le baklava', 'dont tout le', 'monde <em>parle</em>.'], 'en': ['The baklava', 'everyone is', '<em>talking</em> about.']},
              lead=T('Baklava, knafeh préparé à la commande, halawet el jibn et petits fours, joliment emballés pour offrir. Ouvert tous les jours jusqu’à 21 h.',
                     'Baklava, knafeh made to order, halawet el jibn and petit fours, beautifully boxed for gifting. Open every day until 9 p.m.'),
              cta=T('Commander une boîte', 'Order a box'), cta_href='#choose',
              meta=[{'big': T('7 jours', '7 days'), 'small': T('de 10 h à 21 h', '10 a.m. to 9 p.m.')},
                    {'big': T('Knafeh', 'Knafeh'), 'small': T('préparé à la commande', 'made to order')}]),
    marquee=[T('Baklava'), T('Knafeh'), T('Halawet el jibn'), T('Petits fours', 'Petit fours'), T('Boîtes cadeaux', 'Gift boxes')],
    picker=dict(eyebrow=T('Commander', 'Order'), title=T('Qu’est-ce qu’on vous prépare?', 'What can we make for you?'),
                sub=T('Choisissez, envoyez-nous un texto, et votre commande vous attend.', 'Pick one, send us a text, and your order will be waiting.'),
                cta=T('Envoyer un texto', 'Send a text'),
                options=[
                    dict(icon='🎁', img='p1.jpg', src='sw8', title=T('Une boîte cadeau', 'A gift box'), desc=T('Joliment emballée', 'Beautifully packed'),
                         panel_title=T('Joliment emballé, prêt à offrir', 'Beautifully boxed, ready to give'),
                         panel_text=T('Choisissez la taille, on s’occupe du reste.', 'Pick a size, we’ll take care of the rest.'),
                         sms=T('Bonjour, j’aimerais une boîte cadeau (taille: __) pour le __ (date).', 'Hi, I’d like a gift box (size: __) for __ (date).')),
                    dict(icon='🔥', img='p2.jpg', src='sw15', title=T('Un knafeh', 'Knafeh'), desc=T('Préparé à la commande', 'Made to order'),
                         panel_title=T('Knafeh préparé à la commande', 'Knafeh made to order'),
                         panel_text=T('Dites-nous quand vous passez, on le prépare pour votre arrivée.', 'Tell us when you’re coming and we’ll have it ready.'),
                         sms=T('Bonjour, j’aimerais un knafeh pour __ personnes, vers __ h.', 'Hi, I’d like a knafeh for __ people, around __.')),
                    dict(icon='🎉', img='p3.jpg', src='sw13', title=T('Un plateau', 'A party tray'), desc=T('Pour une fête ou un événement', 'For a party or event'),
                         panel_title=T('Un plateau pour recevoir', 'A tray for hosting'),
                         panel_text=T('Nombre d’invités et date, et on compose votre assortiment.', 'Number of guests and the date, and we’ll build your assortment.'),
                         sms=T('Bonjour, j’aimerais un plateau pour __ personnes, le __ (date).', 'Hi, I’d like a tray for __ people, on __ (date).')),
                    dict(icon='☕', img='p4.jpg', src='sw4', title=T('Je passe', 'Dropping by'), desc=T('Ouvert jusqu’à 21 h', 'Open until 9 p.m.'),
                         panel_title=T('Ouvert tous les jours jusqu’à 21 h', 'Open every day until 9 p.m.'),
                         panel_text=T('Venez choisir en vitrine. Il y a toujours du nouveau.', 'Come pick from the display case. There’s always something new.'),
                         sms=T('Bonjour, avez-vous __ aujourd’hui?', 'Hi, do you have __ today?')),
                ]),
    split=dict(img='split.jpg', src='sw7', eyebrow=T('La maison', 'The shop'), title=T('Fait maison, emballé avec soin.', 'Homemade, packed with care.'),
               intro=T('Des pâtisseries arabes faites maison, à savourer sur place ou à offrir.', 'Homemade Arabic pastries, to enjoy or to give.'),
               features=[dict(title=T('Le fameux baklava', 'That famous baklava'), text=T('« Un des meilleurs à Montréal », selon nos clients.', '“One of the best in Montreal,” according to our customers.')),
                         dict(title=T('Knafeh à la commande', 'Knafeh made to order'), text=T('Préparé pour vous, servi chaud.', 'Made for you, served warm.')),
                         dict(title=T('Prêt à offrir', 'Ready to give'), text=T('Des boîtes joliment emballées pour chaque occasion.', 'Beautifully packed boxes for every occasion.'))]),
    gallery_head=dict(eyebrow=T('Nos douceurs', 'Our sweets'), title=T('Une vitrine qui donne faim.', 'A display case worth the trip.'),
                      sub=T('Photos d’exemple. Vos vraies photos les remplaceront.', 'Sample photos. Your real photos will replace them.')),
    gallery=[dict(img='g1.jpg', src='sw9', cap=T('Petits fours', 'Petit fours')), dict(img='g2.jpg', src='sw1', cap=T('Baklava')), dict(img='g3.jpg', src='sw6', cap=T('Douceurs au sirop', 'Syrup sweets')),
             dict(img='g4.jpg', src='sw8', cap=T('Boîtes cadeaux', 'Gift boxes')), dict(img='g5.jpg', src='sw4', cap=T('Fait maison', 'Homemade')), dict(img='g6.jpg', src='sw13', cap=T('Plateaux', 'Trays'))],
    review_block=dict(title=T('77 avis. 4,5 étoiles.', '77 reviews. 4.5 stars.'),
                      text=T('Ce qui revient le plus souvent dans les avis de nos clients:', 'What comes up most in our customers’ reviews:'),
                      themes=[T('Baklava exceptionnel', 'Outstanding baklava'), T('Knafeh'), T('Grand choix', 'Great variety'), T('Service attentionné', 'Helpful service')]),
    visit_title=T('Ouvert tous les jours.', 'Open every day.'), hours=rows, hours_js=js,
    cta=dict(img='cta.jpg', src='sw9', title=T('Une boîte pour ce week-end?', 'A box for this weekend?'), btn=T('Appeler pour commander', 'Call to order')),
)

# ---- GM Appliance Réparation ---------------------------------------------
fq, th = theme('grotesk', bg='#0b1220', surface='#111b2e', text='#eef3fb', muted='#97a3b9', accent='#3fa9ff',
               accent_ink='#04121f', line='rgba(238,243,251,.11)', display_weight=600, display_tracking='-0.03em')
rows, js = hours({d: (0, 1440) for d in range(7)})
B['gm-appliance'] = dict(
    name='GM Appliance', initials='GM', fonts=fq, theme=th, tagline_plain='Réparation d’électroménagers · Ouest-de-l’Île',
    kind=T('Réparation d’électroménagers', 'Appliance repair'),
    phone='514-684-1270', phone_tel='+15146841270', rating='4.8', reviews=110, city='Dollard-des-Ormeaux, QC',
    address='149, rue France<br>Dollard-des-Ormeaux, QC H9A 1K4', address_q='149 Rue France, Dollard-des-Ormeaux, QC H9A 1K4',
    maps_q='Gm Appliance Reparation 149 Rue France Dollard-des-Ormeaux',
    nav=[{'href': '#choose', 'label': T('Réparations', 'Repairs')}, {'href': '#about', 'label': T('Pourquoi GM', 'Why GM')}, {'href': '#visit', 'label': T('Contact', 'Contact')}],
    hero=dict(img='hero.jpg', src='ap1', pos='center',
              eyebrow=T('Ouvert 24 h sur 24 · 7 jours', 'Open 24 hours · 7 days'),
              title={'fr': ['Votre frigo', 'lâche?', 'On <em>arrive</em>.'], 'en': ['Fridge', 'quit on you?', 'We’re <em>on the way</em>.']},
              lead=T('Réfrigérateurs, laveuses, sécheuses et plus, réparés chez vous dans l’Ouest-de-l’Île. On répond au téléphone, on arrive à l’heure, on laisse propre.',
                     'Fridges, washers, dryers and more, repaired at your home across the West Island. We answer the phone, show up on time and leave it clean.'),
              cta=T('Décrire mon problème', 'Describe my problem'), cta_href='#choose',
              meta=[{'big': '24/7', 'small': T('on répond quand vous appelez', 'we answer when you call')},
                    {'big': T('À domicile', 'At home'), 'small': T('partout dans l’Ouest-de-l’Île', 'across the West Island')}]),
    marquee=[T('Réfrigérateurs', 'Refrigerators'), T('Laveuses', 'Washers'), T('Sécheuses', 'Dryers'), T('Lave-vaisselle', 'Dishwashers'), T('Cuisinières', 'Stoves'), T('24/7')],
    picker=dict(eyebrow=T('Réparations', 'Repairs'), title=T('Qu’est-ce qui ne marche plus?', 'What stopped working?'),
                sub=T('Choisissez l’appareil, ajoutez la marque, et envoyez. On vous rappelle rapidement.', 'Pick the appliance, add the brand, and send. We’ll call you back quickly.'),
                cta=T('Envoyer un texto', 'Send a text'),
                options=[
                    dict(icon='🧊', img='p1.jpg', src='ap4', title=T('Réfrigérateur', 'Refrigerator'), desc=T('Ne refroidit plus, fait du bruit, coule', 'Not cooling, noisy, leaking'),
                         panel_title=T('Un frigo qui ne refroidit plus, ça n’attend pas', 'A warm fridge can’t wait'),
                         panel_text=T('Plusieurs clients ont vu leur frigo réparé le jour même. Écrivez-nous la marque et le problème.', 'Many customers had their fridge fixed the same day. Text us the brand and the problem.'),
                         sms=T('Bonjour, mon réfrigérateur (marque: __) ne refroidit plus. Adresse: __', 'Hi, my fridge (brand: __) stopped cooling. Address: __')),
                    dict(icon='🌀', img='p2.jpg', src='ap3', title=T('Laveuse', 'Washer'), desc=T('Ne vidange plus, ne tourne plus', 'Won’t drain, won’t spin'),
                         panel_title=T('Une laveuse qui ne vidange plus?', 'Washer won’t drain?'),
                         panel_text=T('Dites-nous la marque et ce qui se passe. On diagnostique et on répare sur place.', 'Tell us the brand and what’s happening. We diagnose and repair on site.'),
                         sms=T('Bonjour, ma laveuse (marque: __) a un problème: __. Adresse: __', 'Hi, my washer (brand: __) has a problem: __. Address: __')),
                    dict(icon='🔥', img='p3.jpg', src='ap1', title=T('Sécheuse', 'Dryer'), desc=T('Ne chauffe plus, ne tourne plus', 'No heat, won’t tumble'),
                         panel_title=T('Une sécheuse qui ne chauffe plus?', 'Dryer not heating?'),
                         panel_text=T('Souvent une pièce simple à remplacer. Écrivez-nous et on vous dit quoi faire.', 'Often a simple part to replace. Text us and we’ll tell you what’s next.'),
                         sms=T('Bonjour, ma sécheuse (marque: __) ne __. Adresse: __', 'Hi, my dryer (brand: __) won’t __. Address: __')),
                    dict(icon='🔧', img='p4.jpg', src='ap2', title=T('Autre appareil', 'Something else'), desc=T('Lave-vaisselle, cuisinière, four', 'Dishwasher, stove, oven'),
                         panel_title=T('Un autre appareil?', 'Another appliance?'),
                         panel_text=T('Décrivez le problème en une phrase. On vous rappelle.', 'Describe the problem in one sentence. We’ll call you back.'),
                         sms=T('Bonjour, mon __ (appareil, marque) a un problème: __. Adresse: __', 'Hi, my __ (appliance, brand) has a problem: __. Address: __')),
                ]),
    split=dict(img='split.jpg', src='ap5', eyebrow=T('Pourquoi GM', 'Why GM'), title=T('Rapide, honnête, propre.', 'Fast, honest, tidy.'),
               intro=T('Ce que nos clients répètent dans leurs 110 avis.', 'What our customers keep saying in their 110 reviews.'),
               features=[dict(title=T('On répond tout de suite', 'We pick up right away'), text=T('Pas de boîte vocale sans fin. Vous parlez à quelqu’un.', 'No endless voicemail. You talk to a person.')),
                         dict(title=T('On arrive vite', 'We get there fast'), text=T('Des clients nous ont vus arriver en moins d’une heure, et toujours à l’heure dite.', 'Customers have had us at the door within the hour, and on time.')),
                         dict(title=T('Un prix juste', 'A fair price'), text=T('On diagnostique, on explique, puis on répare.', 'We diagnose, explain, then fix.')),
                         dict(title=T('On laisse propre', 'We clean up'), text=T('Réparé, rangé, et on vous laisse tranquille.', 'Fixed, tidied, and out of your way.'))]),
    gallery_head=None, gallery=None,
    review_block=dict(title=T('110 avis. 4,8 étoiles.', '110 reviews. 4.8 stars.'),
                      text=T('Ce qui revient le plus souvent dans les avis de nos clients:', 'What comes up most in our customers’ reviews:'),
                      themes=[T('Rapide', 'Fast'), T('À l’heure', 'On time'), T('Prix juste', 'Fair price'), T('Professionnel', 'Professional'), T('Répond tout de suite', 'Answers right away')]),
    visit_title=T('Appelez, jour et nuit.', 'Call, day or night.'), hours=rows, hours_js=js,
    cta=dict(img='cta.jpg', src='ap2', title=T('Un appareil en panne en ce moment?', 'Appliance broken right now?'), btn=T('Appeler maintenant', 'Call now')),
)

# ---- Rembourrage Demizio -------------------------------------------------
fq, th = theme('playfair', bg='#141210', surface='#1c1916', text='#efe7da', muted='#a59a89', accent='#c9a24a',
               accent_ink='#1a1408', line='rgba(239,231,218,.12)', display_weight=500, display_tracking='-0.015em')
rows, js = hours({1: (H(8), H(18)), 2: (H(8), H(18)), 3: (H(8), H(18)), 4: (H(8), H(18)), 5: (H(8), H(18)), 6: (H(9), H(13)), 0: None})
B['rembourrage-demizio'] = dict(
    name='Rembourrage Demizio', initials='D', fonts=fq, theme=th, tagline_plain='Rembourrage sur mesure · Dollard-des-Ormeaux',
    kind=T('Rembourrage sur mesure', 'Custom upholstery'),
    phone='514-891-9806', phone_tel='+15148919806', rating='5.0', reviews=8, city='Dollard-des-Ormeaux, QC',
    address='4700, boul. des Sources<br>Dollard-des-Ormeaux, QC H8Y 3C4', address_q='4700 Boulevard des Sources, Dollard-des-Ormeaux, QC H8Y 3C4',
    maps_q='Rembourrage Demizio Upholstery 4700 Boulevard des Sources',
    nav=[{'href': '#choose', 'label': T('Soumission', 'Quote')}, {'href': '#gallery', 'label': T('Réalisations', 'Work')}, {'href': '#visit', 'label': T('Atelier', 'Workshop')}],
    hero=dict(img='hero.jpg', src='up6', pos='center',
              eyebrow=T('Atelier de rembourrage · Ouest-de-l’Île', 'Upholstery workshop · West Island'),
              title={'fr': ['Le meuble', 'que vous aimez,', '<em>comme neuf</em>.'], 'en': ['The piece', 'you love,', '<em>made new</em>.']},
              lead=T('Sofas, causeuses, chaises de salle à manger et ottomans recouverts à la main par Joe, un artisan qui aime son métier. Il vous dit tout d’avance.',
                     'Sofas, loveseats, dining chairs and ottomans re-covered by hand by Joe, a craftsman who loves what he does. He tells you everything up front.'),
              cta=T('Envoyer une photo', 'Send a photo'), cta_href='#choose',
              meta=[{'big': T('Artisan', 'Craftsman'), 'small': T('travail fait à la main', 'work done by hand')},
                    {'big': T('Sur mesure', 'Custom'), 'small': T('tissus et finitions', 'fabrics and finishes')}]),
    marquee=[T('Sofas'), T('Causeuses', 'Loveseats'), T('Chaises', 'Dining chairs'), T('Ottomans'), T('Fauteuils', 'Armchairs'), T('Fait à la main', 'Handmade')],
    picker=dict(eyebrow=T('Soumission', 'Get a quote'), title=T('Qu’est-ce qu’on recouvre?', 'What are we re-covering?'),
                sub=T('Choisissez, puis envoyez une photo par texto. Joe vous répond avec une idée du travail.', 'Pick one, then text a photo. Joe will get back to you with what it involves.'),
                cta=T('Envoyer une photo', 'Text a photo'),
                options=[
                    dict(icon='🛋️', img='p1.jpg', src='up4', title=T('Un sofa ou une causeuse', 'A sofa or loveseat'), desc=T('Nouveau tissu, nouvelle mousse', 'New fabric, new foam'),
                         panel_title=T('Votre sofa, comme au premier jour', 'Your sofa, like the day you got it'),
                         panel_text=T('Envoyez une photo du sofa et ses dimensions. On en parle.', 'Send a photo of the sofa and its size. We’ll talk it through.'),
                         sms=T('Bonjour Joe, j’aimerais faire recouvrir un sofa. Je vous envoie une photo.', 'Hi Joe, I’d like to have a sofa re-covered. Sending a photo.')),
                    dict(icon='🪑', img='p2.jpg', src='up7', title=T('Des chaises', 'Dining chairs'), desc=T('Salle à manger, comptoir', 'Dining or counter'),
                         panel_title=T('Six chaises? Aucun problème', 'Six chairs? No problem'),
                         panel_text=T('Des chaises refaites rapidement, avec un fini impeccable.', 'Chairs redone quickly, with a flawless finish.'),
                         sms=T('Bonjour Joe, j’ai __ chaises à faire recouvrir. Je vous envoie une photo.', 'Hi Joe, I have __ chairs to re-cover. Sending a photo.')),
                    dict(icon='🪶', img='p3.jpg', src='up1', title=T('Un fauteuil', 'An armchair'), desc=T('Un meuble de famille à sauver', 'A family piece worth saving'),
                         panel_title=T('Un meuble qui a une histoire', 'A piece with a story'),
                         panel_text=T('On garde ce que vous aimez, on refait le reste.', 'We keep what you love and redo the rest.'),
                         sms=T('Bonjour Joe, j’ai un fauteuil à refaire. Je vous envoie une photo.', 'Hi Joe, I have an armchair to redo. Sending a photo.')),
                    dict(icon='🧵', img='p4.jpg', src='up2', title=T('Autre chose', 'Something else'), desc=T('Ottoman, tête de lit, banc', 'Ottoman, headboard, bench'),
                         panel_title=T('Un projet différent?', 'Something different?'),
                         panel_text=T('Envoyez une photo et quelques mots. Joe vous dit franchement ce qui est possible.', 'Send a photo and a few words. Joe will tell you honestly what’s possible.'),
                         sms=T('Bonjour Joe, j’ai un projet: __. Je vous envoie une photo.', 'Hi Joe, I have a project: __. Sending a photo.')),
                ]),
    split=dict(img='split.jpg', src='up3', eyebrow=T('L’atelier', 'The workshop'), title=T('Un savoir-faire rare.', 'A rare craft.'),
               intro=T('« Difficile de trouver une qualité pareille aujourd’hui », écrit un client. Voici pourquoi.', '“Hard to find quality like this anymore,” one customer wrote. Here’s why.'),
               features=[dict(title=T('Un vrai artisan', 'A true craftsman'), text=T('Joe aime son métier, et ça paraît dans chaque couture.', 'Joe loves what he does, and it shows in every seam.')),
                         dict(title=T('Tout est dit d’avance', 'Everything up front'), text=T('Le travail, le délai, le prix: vous savez à quoi vous attendre.', 'The work, the timing, the price: you know what to expect.')),
                         dict(title=T('Un fini impeccable', 'A flawless finish'), text=T('Des meubles qui ont l’air neufs, pour des années.', 'Furniture that looks new for years.'))]),
    gallery_head=dict(eyebrow=T('Réalisations', 'Our work'), title=T('Tissus, textures, détails.', 'Fabrics, textures, details.'),
                      sub=T('Photos d’exemple. Vos vraies réalisations les remplaceront.', 'Sample photos. Your real projects will replace them.')),
    gallery=[dict(img='g1.jpg', src='up4', cap=T('Sofa en velours', 'Velvet sofa')), dict(img='g2.jpg', src='up2', cap=T('Capitonnage', 'Tufting')), dict(img='g3.jpg', src='up1', cap=T('Fauteuil', 'Armchair')),
             dict(img='g4.jpg', src='up7', cap=T('Chaises', 'Chairs')), dict(img='g5.jpg', src='up8', cap=T('Moderne', 'Modern')), dict(img='g6.jpg', src='up3', cap=T('Choix de tissus', 'Fabric selection'))],
    review_block=dict(title=T('Une note parfaite de 5,0.', 'A perfect 5.0 rating.'),
                      text=T('Ce qui revient le plus souvent dans les avis de nos clients:', 'What comes up most in our customers’ reviews:'),
                      themes=[T('Un maître artisan', 'A master craftsman'), T('Travail magnifique', 'Beautiful work'), T('Délais rapides', 'Fast turnaround'), T('Transparent', 'Upfront')]),
    visit_title=T('Passez à l’atelier.', 'Visit the workshop.'), hours=rows, hours_js=js,
    cta=dict(img='cta.jpg', src='up5', title=T('Un meuble à sauver?', 'A piece worth saving?'), btn=T('Appeler Joe', 'Call Joe')),
)

# ---- Garage Fredmir ------------------------------------------------------
fq, th = theme('barlow', bg='#0b1420', surface='#101c2b', text='#eef2f7', muted='#95a3b5', accent='#f26a1b',
               accent_ink='#ffffff', line='rgba(238,242,247,.11)', display_weight=700, display_tracking='0', display_upper=True, em_style='normal')
rows, js = hours({1: (H(8), H(17)), 2: (H(8), H(17)), 3: (H(8), H(17)), 4: (H(8), H(17)), 5: (H(8), H(17)), 6: None, 0: None})
B['garage-fredmir'] = dict(
    name='Garage Fredmir', initials='GF', fonts=fq, theme=th, tagline_plain='Mécanique générale · Pierrefonds',
    kind=T('Mécanique générale', 'Auto repair'),
    phone='514-626-0888', phone_tel='+15146260888', rating='4.7', reviews=343, city='Pierrefonds, QC',
    address='13070, boul. de Pierrefonds<br>Pierrefonds, QC H9A 1A5', address_q='13070 Boulevard de Pierrefonds, Pierrefonds, QC H9A 1A5',
    maps_q='Garage Fredmir 13070 Boulevard de Pierrefonds',
    nav=[{'href': '#choose', 'label': T('Rendez-vous', 'Book')}, {'href': '#about', 'label': T('Pourquoi nous', 'Why us')}, {'href': '#visit', 'label': T('Nous trouver', 'Visit')}],
    hero=dict(img='hero.jpg', src='mc6', pos='center',
              eyebrow=T('Pneus d’hiver obligatoires le 1er décembre', 'Winter tires required December 1'),
              title={'fr': ['Du travail', 'honnête.', '<em>Des prix justes.</em>'], 'en': ['Honest', 'work.', '<em>Fair prices.</em>']},
              lead=T('Pneus, freins, entretien et diagnostic pour toutes les marques. On vous explique le problème et le prix avant de commencer.',
                     'Tires, brakes, maintenance and diagnostics for every make. We explain the problem and the price before we start.'),
              cta=T('Prendre rendez-vous', 'Book a visit'), cta_href='#choose',
              meta=[{'big': T('Toutes marques', 'All makes'), 'small': T('entretien et réparations', 'maintenance and repairs')},
                    {'big': T('Prix d’avance', 'Price up front'), 'small': T('avant le début des travaux', 'before any work starts')}]),
    marquee=[T('Pneus', 'Tires'), T('Freins', 'Brakes'), T('Entretien', 'Maintenance'), T('Diagnostic', 'Diagnostics'), T('Suspension'), T('Toutes marques', 'All makes')],
    picker=dict(eyebrow=T('Rendez-vous', 'Book'), title=T('De quoi votre auto a besoin?', 'What does your car need?'),
                sub=T('Choisissez, envoyez un texto, on vous confirme une heure.', 'Pick one, send a text, and we’ll confirm a time.'),
                cta=T('Envoyer un texto', 'Send a text'),
                options=[
                    dict(icon='❄️', img='p1.jpg', src='mc5', title=T('Pneus d’hiver', 'Winter tires'), desc=T('Pose, balancement, crevaison', 'Install, balance, flat repair'),
                         panel_title=T('Avant la course du 1er décembre', 'Beat the December 1 rush'),
                         panel_text=T('Les pneus d’hiver sont obligatoires au Québec du 1er décembre au 15 mars. Réservez maintenant.', 'Winter tires are required in Quebec from December 1 to March 15. Book now.'),
                         sms=T('Bonjour, j’aimerais un rendez-vous pour mes pneus d’hiver. Auto: __', 'Hi, I’d like to book a winter tire change. Car: __')),
                    dict(icon='🛑', img='p2.jpg', src='mc3', title=T('Freins', 'Brakes'), desc=T('Bruit, vibration, pédale molle', 'Squeal, shake, soft pedal'),
                         panel_title=T('Des freins qui grincent?', 'Squeaky brakes?'),
                         panel_text=T('On inspecte, on vous dit ce qui presse et ce qui peut attendre.', 'We inspect and tell you what’s urgent and what can wait.'),
                         sms=T('Bonjour, mes freins font __. Auto: __', 'Hi, my brakes are __. Car: __')),
                    dict(icon='⚠️', img='p3.jpg', src='mc2', title=T('Un voyant allumé', 'A warning light'), desc=T('Moteur, ABS, batterie', 'Engine, ABS, battery'),
                         panel_title=T('Un voyant allumé?', 'Warning light on?'),
                         panel_text=T('On trouve la cause et on vous explique avant de réparer.', 'We find the cause and explain it before we fix anything.'),
                         sms=T('Bonjour, le voyant __ est allumé. Auto: __', 'Hi, my __ light is on. Car: __')),
                    dict(icon='🛢️', img='p4.jpg', src='mc1', title=T('Entretien', 'Maintenance'), desc=T('Huile, filtres, inspection', 'Oil, filters, inspection'),
                         panel_title=T('Laissez-la le matin', 'Drop it off in the morning'),
                         panel_text=T('Récupérez-la avant la fermeture, avec le prix confirmé d’avance.', 'Pick it up before closing, with the price confirmed up front.'),
                         sms=T('Bonjour, j’aimerais un rendez-vous pour un entretien. Auto: __', 'Hi, I’d like to book a maintenance visit. Car: __')),
                ]),
    split=dict(img='split.jpg', src='mc8', eyebrow=T('Pourquoi Fredmir', 'Why Fredmir'), title=T('Ce que nos clients disent.', 'What our customers say.'),
               intro=T('Des clients fidèles depuis l’ouverture, et 343 avis pour le prouver.', 'Customers who’ve been coming since day one, and 343 reviews to show for it.'),
               features=[dict(title=T('Honnêteté', 'Honesty'), text=T('On vous dit ce qui doit être réparé, et ce qui peut attendre.', 'We tell you what needs fixing, and what can wait.')),
                         dict(title=T('Prix justes', 'Fair prices'), text=T('Le prix est confirmé avant le début des travaux.', 'The price is confirmed before work starts.')),
                         dict(title=T('Rapidité', 'Speed'), text=T('Laissez votre auto le matin, récupérez-la avant la fermeture.', 'Drop your car off in the morning, pick it up before closing.'))]),
    gallery_head=None, gallery=None,
    review_block=dict(title=T('343 avis. 4,7 étoiles.', '343 reviews. 4.7 stars.'),
                      text=T('Ce qui revient le plus souvent dans les avis de nos clients:', 'What comes up most in our customers’ reviews:'),
                      themes=[T('Honnête', 'Honest'), T('Rapide', 'Fast'), T('Meilleurs prix', 'Best prices'), T('Fidèles depuis l’ouverture', 'Loyal since day one')]),
    visit_title=T('Passez au garage.', 'Come by the shop.'), hours=rows, hours_js=js,
    cta=dict(img='cta.jpg', src='mc7', title=T('Pneus d’hiver: 1er décembre.', 'Winter tires: December 1.'), btn=T('Réserver mon changement', 'Book my tire change')),
)

# ---------------------------------------------------------------- build
def save_img(src, dst, width):
    im = Image.open(os.path.join(STOCK, src + '.jpg')).convert('RGB')
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(dst, quality=80, optimize=True, progressive=True)

def build(slug):
    c = B[slug]
    out = os.path.join(OUT, slug); img = os.path.join(out, 'img')
    if os.path.isdir(img):
        shutil.rmtree(img)
    os.makedirs(img, exist_ok=True)
    save_img(c['hero']['src'], os.path.join(img, c['hero']['img']), 2200)
    for o in c['picker']['options']:
        save_img(o['src'], os.path.join(img, o['img']), 1400)
    save_img(c['split']['src'], os.path.join(img, c['split']['img']), 1400)
    for g in (c.get('gallery') or []):
        save_img(g['src'], os.path.join(img, g['img']), 1400)
    save_img(c['cta']['src'], os.path.join(img, c['cta']['img']), 1800)
    segno.make(f'https://coughlindigital.ca/demo/{slug}/', error='m').save(os.path.join(out, 'qr.png'), scale=10, border=2)
    env = Environment(loader=FileSystemLoader(HERE), autoescape=False)
    r = float(c['rating']); full = round(r)
    c['stars'] = '★' * full + '☆' * (5 - full)
    html = env.get_template('template.html').render(**c)
    open(os.path.join(out, 'index.html'), 'w').write(html)
    print('built', slug)

if __name__ == '__main__':
    lib = os.path.join(OUT, '_lib'); os.makedirs(lib, exist_ok=True)
    for f in ('gsap.min.js', 'ScrollTrigger.min.js', 'lenis.min.js'):
        shutil.copy(os.path.join(HERE, f), lib)
    for s in (sys.argv[1:] or B.keys()):
        build(s)
