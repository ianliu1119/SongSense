"""
Expand the song catalog to ~500 songs and fetch iTunes 30-second preview URLs.
Also back-fills preview URLs for the existing modern songs (IDs 11-20).

Run:  python3 expand_db.py
"""

import json, sqlite3, time, urllib.request, urllib.parse
from pathlib import Path

DB_PATH = Path(__file__).parent / "songfinder.db"

# (title, artist, year, [genres], lyric_snippet, [mood_keywords], description)
NEW_SONGS = [
    # ── POP – CLASSIC ─────────────────────────────────────────────────────────
    ("Thriller", "Michael Jackson", 1982, ["pop","funk","dance"], "It's close to midnight", ["spooky","danceable","iconic","groovy","dramatic"], "Funky horror-themed pop with a landmark Vincent Price spoken-word breakdown."),
    ("Beat It", "Michael Jackson", 1983, ["pop","rock"], "Beat it, beat it", ["edgy","driving","guitar","anthemic","rebellious"], "Rock-infused pop with an Eddie Van Halen guitar solo and gang-fight urgency."),
    ("Purple Rain", "Prince", 1984, ["pop","rock","R&B"], "Never meant to cause you any sorrow", ["emotional","epic","romantic","guitar","ballad"], "Epic power ballad drenched in electric guitar and raw emotional longing."),
    ("Like a Prayer", "Madonna", 1989, ["pop"], "Life is a mystery, everyone must stand alone", ["gospel","dramatic","uplifting","powerful","controversial"], "Gospel-infused pop anthem with soaring choir and dramatic crescendo."),
    ("Material Girl", "Madonna", 1984, ["pop","dance"], "We are living in a material world", ["playful","catchy","80s","danceable","retro"], "Tongue-in-cheek 80s pop with a bubbly disco-inspired groove."),
    ("Papa Don't Preach", "Madonna", 1986, ["pop"], "Papa don't preach, I'm in trouble deep", ["emotional","dramatic","defiant","80s","storytelling"], "Dramatic pop narrative about teen pregnancy with string-backed urgency."),
    ("Girls Just Want to Have Fun", "Cyndi Lauper", 1983, ["pop"], "Girls just want to have fun", ["fun","upbeat","carefree","80s","anthemic"], "Carefree 80s anthem celebrating female freedom and playfulness."),
    ("Time After Time", "Cyndi Lauper", 1983, ["pop","synth-pop"], "If you're lost you can look and you will find me", ["tender","romantic","nostalgic","gentle","80s"], "Soft, tender 80s synth-pop ballad about steadfast love and loyalty."),
    ("Sweet Dreams (Are Made of This)", "Eurythmics", 1983, ["synth-pop","new wave"], "Sweet dreams are made of this", ["hypnotic","synthy","dark","driving","iconic"], "Cold, hypnotic synth-pop with a relentless mechanical beat and eerie vocals."),
    ("Don't You (Forget About Me)", "Simple Minds", 1985, ["pop","new wave"], "Don't you forget about me", ["anthemic","nostalgic","80s","yearning","cinematic"], "Soaring 80s new-wave anthem forever linked to The Breakfast Club."),
    ("Take On Me", "A-ha", 1985, ["synth-pop"], "Take on me, take me on", ["bright","catchy","80s","romantic","upbeat"], "Infectiously bright synth-pop with a soaring falsetto chorus."),
    ("Don't Stop Believin'", "Journey", 1981, ["rock","pop"], "Don't stop believin', hold on to the feeling", ["anthemic","uplifting","classic-rock","hopeful","singalong"], "Classic rock anthem of perseverance driven by an iconic piano intro."),
    ("Africa", "Toto", 1982, ["pop","rock"], "I hear the drums echoing tonight", ["atmospheric","nostalgic","melodic","lush","journey"], "Lush, melodic 80s pop with exotic percussion and sweeping harmonies."),
    ("Every Breath You Take", "The Police", 1983, ["pop","rock"], "Every breath you take, every move you make", ["obsessive","dark","romantic","melodic","minimal"], "Deceptively gentle pop song with an obsessive, watchful undercurrent."),
    ("Roxanne", "The Police", 1978, ["rock","reggae","new wave"], "Roxanne, you don't have to put on the red light", ["urgent","passionate","reggae-rock","raw","tense"], "Urgent, reggae-inflected rock about a man pleading with a street worker."),
    ("With or Without You", "U2", 1987, ["rock","pop"], "And you give yourself away", ["yearning","emotional","anthemic","building","melancholic"], "Aching U2 ballad that builds from near-silence to emotional release."),
    ("Where the Streets Have No Name", "U2", 1987, ["rock","post-punk"], "", ["epic","anthemic","soaring","uplifting","stadium"], "Epic, soaring U2 anthem built on a shimmering Edge guitar riff and Bono's yearning vocals."),
    ("Fast Car", "Tracy Chapman", 1988, ["folk","pop"], "You got a fast car", ["hopeful","bittersweet","storytelling","acoustic","emotional"], "Quietly devastating folk-pop narrative about escaping poverty with sparse acoustic guitar."),
    ("I Want It That Way", "Backstreet Boys", 1999, ["pop"], "Tell me why, ain't nothin' but a heartache", ["romantic","melodic","boyband","catchy","90s"], "Smooth boy-band pop with layered harmonies and a singalong chorus."),
    ("Baby One More Time", "Britney Spears", 1998, ["pop","dance"], "My loneliness is killing me", ["catchy","danceable","upbeat","90s","iconic"], "Punchy, era-defining teen pop with a driving beat and instantly memorable hook."),
    ("Toxic", "Britney Spears", 2003, ["pop","dance"], "Baby, can't you see, I'm calling", ["seductive","driving","danceable","strings","electropop"], "Sleek electro-pop with Bond-film strings and an irresistibly seductive groove."),
    ("Oops!... I Did It Again", "Britney Spears", 2000, ["pop"], "I played with your heart, got lost in the game", ["playful","catchy","upbeat","bubbly","flirtatious"], "Bubbly early-00s pop with a punchy chorus and playful confession."),
    ("Bye Bye Bye", "*NSYNC", 2000, ["pop","dance"], "Bye bye bye", ["upbeat","danceable","90s","punchy","energetic"], "High-energy boy-band pop with punchy brass stabs and a defiant attitude."),
    ("...Baby One More Time", "Britney Spears", 1998, ["pop"], "", ["iconic","teen-pop","catchy","upbeat","90s"], "Genre-defining debut with a driving schoolgirl aesthetic and earworm chorus."),
    ("Waterfalls", "TLC", 1994, ["R&B","pop"], "Don't go chasing waterfalls", ["soulful","message","melodic","smooth","90s"], "Smooth R&B with a cautionary message delivered over a gentle, flowing groove."),
    ("No Scrubs", "TLC", 1999, ["R&B","pop"], "I don't want no scrubs", ["funky","attitude","catchy","confident","90s"], "Funky, attitude-filled R&B that became an anthem of female empowerment."),
    ("Genie in a Bottle", "Christina Aguilera", 1999, ["pop","R&B"], "I feel like I've been locked up tight", ["flirtatious","smooth","90s","catchy","upbeat"], "Smooth debut pop single with a hint of R&B and a confident, flirty tone."),
    ("Beautiful", "Christina Aguilera", 2002, ["pop","ballad"], "I am beautiful, no matter what they say", ["empowering","emotional","piano","uplifting","heartfelt"], "Piano-led empowerment ballad with a soaring vocal performance."),
    ("Complicated", "Avril Lavigne", 2002, ["pop","rock"], "Chill out, whatcha yelling for", ["angsty","catchy","teen","guitar","relatable"], "Punchy pop-rock anthem capturing teenage frustration with inauthenticity."),
    ("Sk8er Boi", "Avril Lavigne", 2002, ["pop","punk"], "He was a boy, she was a girl", ["punk","upbeat","guitar","teen","fun"], "Breezy pop-punk with a three-chord guitar hook and a cheeky love story."),
    ("Since U Been Gone", "Kelly Clarkson", 2004, ["pop","rock"], "But since you been gone, I can breathe for the first time", ["catchy","anthemic","upbeat","empowering","guitar"], "Explosive pop-rock breakup anthem with massive singalong energy."),
    ("Irreplaceable", "Beyoncé", 2006, ["pop","R&B"], "To the left, to the left", ["empowering","soulful","confident","catchy","breakup"], "Breezy, confident breakup song with an effortlessly cool R&B swing."),
    ("Halo", "Beyoncé", 2008, ["pop","R&B"], "Remember those walls I built", ["uplifting","romantic","soaring","emotional","ballad"], "Sweeping romantic ballad with an uplifting gospel-tinged chorus."),
    ("Crazy in Love", "Beyoncé", 2003, ["R&B","pop","hip-hop"], "Got me looking so crazy right now", ["energetic","sexy","iconic","hip-hop","danceable"], "High-energy R&B with a brassy horn sample, rap verse from Jay-Z, and irresistible energy."),
    ("Umbrella", "Rihanna", 2007, ["pop","R&B","dance"], "Now that it's raining more than ever", ["catchy","danceable","smooth","upbeat","iconic"], "Sleek, addictive pop with a distinctive spoken intro and an endlessly catchy hook."),
    ("We Found Love", "Rihanna", 2011, ["dance","EDM","pop"], "We found love in a hopeless place", ["euphoric","danceable","EDM","uplifting","emotional"], "Euphoric EDM-pop with a Calvin Harris drop and Rihanna's airy vocals over a pulsing beat."),
    ("Diamonds", "Rihanna", 2012, ["pop","R&B"], "Shine bright like a diamond", ["ethereal","uplifting","dreamy","anthemic","smooth"], "Dreamy, atmospheric pop with a soaring chorus and minimalist production."),
    ("Poker Face", "Lady Gaga", 2008, ["pop","dance","electropop"], "Can't read my, can't read my poker face", ["danceable","electro","catchy","driven","provocative"], "Driving electro-pop with a relentless beat and provocative lyrical wordplay."),
    ("Bad Romance", "Lady Gaga", 2009, ["pop","dance","electropop"], "I want your love and I want your revenge", ["dramatic","danceable","iconic","anthemic","operatic"], "Operatic electro-pop with a sweeping hook and theatrically dramatic production."),
    ("Just Dance", "Lady Gaga", 2008, ["pop","dance"], "Just dance, gonna be okay", ["fun","danceable","electro","upbeat","carefree"], "Carefree, euphoric electro-pop debut built for the dancefloor."),
    ("Call Me Maybe", "Carly Rae Jepsen", 2012, ["pop"], "Hey, I just met you, and this is crazy", ["bubbly","catchy","innocent","upbeat","summer"], "Irresistibly bubbly summer pop with an instantly memorable hook."),
    ("Roar", "Katy Perry", 2013, ["pop"], "I got the eye of the tiger", ["empowering","upbeat","anthemic","catchy","confident"], "Bold empowerment anthem with an arena-ready chorus and motivational lyrics."),
    ("Teenage Dream", "Katy Perry", 2010, ["pop","synth-pop"], "You think I'm pretty without any makeup on", ["dreamy","romantic","upbeat","synthy","summer"], "Dreamy, nostalgic synth-pop celebrating the rush of young love."),
    ("Firework", "Katy Perry", 2010, ["pop"], "Do you ever feel like a plastic bag", ["uplifting","anthemic","empowering","emotional","ballad"], "Soaring empowerment anthem that builds from self-doubt to explosive release."),
    ("Party Rock Anthem", "LMFAO", 2011, ["dance","electropop","hip-hop"], "Party rock is in the house tonight", ["fun","danceable","electro","silly","energetic"], "Absurdly fun electro-hop with a shuffling dance breakdown and party energy."),
    ("Somebody That I Used to Know", "Gotye", 2011, ["indie-pop","alternative"], "Now and then I think of when we were together", ["melancholic","bittersweet","indie","acoustic","emotional"], "Melancholic indie-pop breakup song with a distinctive xylophone riff."),
    ("Happy", "Pharrell Williams", 2013, ["pop","soul","funk"], "Clap along if you feel like a room without a roof", ["upbeat","joyful","feel-good","danceable","funk"], "Infectious, feel-good neo-soul with a hand-clapping groove and pure optimism."),
    ("Uptown Funk", "Mark Ronson ft. Bruno Mars", 2014, ["funk","pop","R&B"], "Don't believe me just watch", ["groovy","funky","danceable","retro","energetic"], "Irresistibly funky retro-soul throwback with Bruno Mars's charismatic delivery."),
    ("Thinking Out Loud", "Ed Sheeran", 2014, ["pop","soul"], "Take me into your loving arms", ["romantic","smooth","soulful","ballad","acoustic"], "Warm, soulful acoustic love song with a Stevie Wonder-inspired feel."),
    ("Photograph", "Ed Sheeran", 2014, ["pop","acoustic"], "Loving can hurt, loving can hurt sometimes", ["nostalgic","romantic","acoustic","heartfelt","emotional"], "Tender acoustic ballad about holding onto distant loved ones through memory."),
    ("Love Yourself", "Justin Bieber", 2015, ["pop","acoustic"], "And I didn't wanna write a song", ["catchy","acoustic","breakup","witty","bitter"], "Breezy acoustic breakup song with understated wit and a light folk touch."),
    ("Sorry", "Justin Bieber", 2015, ["pop","dance"], "Is it too late now to say sorry", ["upbeat","danceable","90s-house","catchy","apologetic"], "Surprisingly upbeat apology song built on a bouncy 90s house-inflected groove."),
    ("What Do You Mean?", "Justin Bieber", 2015, ["pop","tropical"], "What do you mean? When you nod your head yes", ["tropical","catchy","midtempo","uncertain","smooth"], "Breezy tropical-influenced pop with a swaying midtempo groove."),
    ("Can't Stop the Feeling!", "Justin Timberlake", 2016, ["pop","funk","soul"], "I got this feeling inside my bones", ["joyful","danceable","fun","funk","feel-good"], "Irresistibly joyful pop-funk built to fill dancefloors and movie soundtracks alike."),
    ("Levitating", "Dua Lipa", 2020, ["pop","disco"], "I got you, moonlight, you're my starlight", ["euphoric","disco","danceable","upbeat","glittery"], "Glittery disco-pop with a propulsive groove and cosmic romantic imagery."),
    ("New Rules", "Dua Lipa", 2017, ["pop","electropop"], "One, don't pick up the phone", ["empowering","upbeat","catchy","danceable","confident"], "Catchy electro-pop breakup anthem structured around self-imposed relationship rules."),
    ("Don't Start Now", "Dua Lipa", 2019, ["pop","disco","dance"], "If you don't wanna see me dancing with somebody", ["danceable","confident","disco","upbeat","cool"], "Slick nu-disco with a pulsing bassline and cool, unbothered attitude."),
    ("drivers license", "Olivia Rodrigo", 2021, ["pop","ballad"], "I got my driver's license last week", ["heartbroken","cinematic","piano","emotional","teenage"], "Devastating teenage heartbreak ballad that builds from whisper to a cathartic scream."),
    ("good 4 u", "Olivia Rodrigo", 2021, ["pop","punk"], "Good for you, you look happy and healthy", ["angry","pop-punk","catchy","sarcastic","energetic"], "Biting pop-punk with sarcastic lyrics and a crunchy guitar drop."),
    ("As It Was", "Harry Styles", 2022, ["pop","synth-pop"], "Holdin' me back, gravity's holdin' me back", ["nostalgic","upbeat","emotional","80s-inspired","bittersweet"], "Shimmering 80s-inspired pop with an upbeat pulse that masks emotional melancholy."),
    ("Watermelon Sugar", "Harry Styles", 2019, ["pop","rock"], "Tastes like strawberries on a summer evening", ["feel-good","summer","groovy","romantic","retro"], "Sun-soaked, feel-good pop with a warm retro groove and hedonistic imagery."),
    ("Bad Guy", "Billie Eilish", 2019, ["pop","electropop"], "I'm the bad guy, duh", ["minimalist","dark","quirky","bass-heavy","cool"], "Subversive whisper-pop with a trap-influenced bass drop and playfully dark attitude."),
    ("Ocean Eyes", "Billie Eilish", 2016, ["pop","indie"], "I've been watching you for some time", ["ethereal","dreamy","delicate","sad","intimate"], "Delicate, ethereal bedroom-pop with haunting vocals and cinematic longing."),
    ("Heat Waves", "Glass Animals", 2020, ["indie-pop","psychedelic"], "Sometimes, all I think about is you", ["dreamy","nostalgic","hypnotic","psychedelic","bittersweet"], "Hypnotic, hazy indie-pop with psychedelic production and aching summer nostalgia."),
    ("Blinding Lights", "The Weeknd", 2019, ["synth-pop","pop"], "I've been on my own for long enough", ["euphoric","80s","synthy","driving","nostalgic"], "Euphoric 80s-inspired synth-pop with a pulsing beat and neon-lit midnight energy."),
    ("Save Your Tears", "The Weeknd", 2020, ["synth-pop","pop"], "I saw you dancing in a crowded room", ["melancholic","80s","melodic","bittersweet","catchy"], "Melancholic 80s-flavored pop with a bittersweet hook and polished synth production."),
    ("Starboy", "The Weeknd", 2016, ["R&B","pop","electro"], "I'm tryna put you in the worst mood", ["dark","moody","cool","electro-R&B","nocturnal"], "Dark, sleek electro-R&B with Daft Punk production and a menacing cool."),
    # ── ROCK – CLASSIC ────────────────────────────────────────────────────────
    ("Hotel California", "Eagles", 1977, ["rock","classic rock"], "On a dark desert highway, cool wind in my hair", ["mysterious","atmospheric","classic-rock","guitar","storytelling"], "Mysterious classic rock epic with a layered dual-guitar outro and vivid storytelling."),
    ("Stairway to Heaven", "Led Zeppelin", 1971, ["rock","hard rock"], "There's a lady who's sure all that glitters is gold", ["epic","mystical","guitar","building","progressive"], "Epic rock suite that evolves from delicate acoustic fingerpicking to thunderous electric climax."),
    ("Whole Lotta Love", "Led Zeppelin", 1969, ["hard rock","blues rock"], "You need coolin', baby, I'm not foolin'", ["raw","driving","bluesy","heavy","psychedelic"], "Raw, riff-driven hard rock with a psychedelic middle section and unstoppable energy."),
    ("Black Dog", "Led Zeppelin", 1971, ["hard rock","blues rock"], "Hey, hey, mama, said the way you move", ["riff-based","heavy","raw","swaggering","complex"], "Intricate, stop-start hard rock built on one of rock's most recognizable riffs."),
    ("Sweet Child O' Mine", "Guns N' Roses", 1987, ["rock","hard rock"], "She's got a smile that it seems to me", ["anthemic","guitar","romantic","hard-rock","iconic"], "Hard-rock anthem with a world-famous arpeggiated guitar intro and raw emotional power."),
    ("Paradise City", "Guns N' Roses", 1987, ["rock","hard rock"], "Take me down to the paradise city", ["anthemic","driving","energetic","guitar","singalong"], "Driving hard-rock anthem that accelerates from a gentle intro to a frantic finale."),
    ("Welcome to the Jungle", "Guns N' Roses", 1987, ["rock","hard rock"], "Welcome to the jungle, we got fun and games", ["aggressive","dark","energetic","guitar","dangerous"], "Aggressive, snarling hard-rock opener that captures the menace of city life."),
    ("Enter Sandman", "Metallica", 1991, ["metal","hard rock"], "Say your prayers, little one", ["dark","heavy","driving","iconic","menacing"], "Crushing metal anthem with a hypnotic riff and nightmarish imagery of childhood fears."),
    ("Nothing Else Matters", "Metallica", 1991, ["metal","rock","ballad"], "So close, no matter how far", ["emotional","guitar","ballad","tender","intimate"], "Surprisingly tender metal ballad with fingerpicked guitar and heartfelt sincerity."),
    ("One", "Metallica", 1988, ["metal","hard rock"], "I can't remember anything", ["dark","heavy","emotional","progressive","war"], "Intense anti-war metal epic that builds from quiet acoustic despair to crushing speed."),
    ("Paranoid", "Black Sabbath", 1970, ["metal","hard rock"], "Finished with my woman 'cause she couldn't help me with my mind", ["heavy","dark","fast","riff-based","proto-metal"], "Fast, riff-driven proto-metal with bleak lyrics that defined the heavy metal template."),
    ("Back in Black", "AC/DC", 1980, ["rock","hard rock"], "Back in black, I hit the sack", ["driving","anthemic","riff-based","energetic","classic"], "Thunderous rock anthem built on one of the most iconic guitar riffs in history."),
    ("Highway to Hell", "AC/DC", 1979, ["rock","hard rock"], "Living easy, living free", ["fun","driving","anthemic","hard-rock","rebellious"], "Relentlessly fun hard-rock party anthem with a deceptively simple but irresistible riff."),
    ("Purple Haze", "Jimi Hendrix", 1967, ["rock","psychedelic","blues rock"], "Excuse me while I kiss the sky", ["psychedelic","guitar","raw","mind-bending","bluesy"], "Psychedelic blues-rock with Hendrix's revolutionary guitar technique front and center."),
    ("All Along the Watchtower", "Jimi Hendrix", 1968, ["rock","blues rock","psychedelic"], "There must be some kind of way outta here", ["atmospheric","bluesy","psychedelic","guitar","Dylan"], "Searing Hendrix reimagining of Dylan's song with cosmic, churning guitar work."),
    ("Mr. Tambourine Man", "Bob Dylan", 1965, ["folk","rock"], "Hey! Mr. Tambourine Man, play a song for me", ["poetic","folk","dreamlike","acoustic","literary"], "Poetic, dreamlike folk masterpiece with surrealist imagery and hypnotic acoustic guitar."),
    ("Like a Rolling Stone", "Bob Dylan", 1965, ["rock","folk rock"], "Once upon a time you dressed so fine", ["confrontational","epic","organ","literary","raw"], "Landmark 6-minute rock song with a biting, confrontational lyric and swirling organ."),
    ("(I Can't Get No) Satisfaction", "The Rolling Stones", 1965, ["rock","blues rock"], "I can't get no satisfaction", ["rebellious","riff-based","raw","anthemic","classic"], "Fuzztone guitar riff and rebellious attitude that captured the spirit of 60s discontent."),
    ("Paint It Black", "The Rolling Stones", 1966, ["rock","psychedelic"], "I see a red door and I want it painted black", ["dark","hypnotic","sitar","melancholic","moody"], "Dark, hypnotic rock with a sitar riff and bleak romantic loss."),
    ("Jumpin' Jack Flash", "The Rolling Stones", 1968, ["rock","blues rock"], "I was born in a cross-fire hurricane", ["driving","raw","riff-based","energetic","bluesy"], "Stomping blues-rock riff monster with a joyfully menacing energy."),
    ("Hey Jude", "The Beatles", 1968, ["pop","rock"], "Hey Jude, don't make it bad", ["uplifting","anthemic","singalong","emotional","classic"], "Uplifting Beatles anthem with a simple message and an enormous, sing-along coda."),
    ("Let It Be", "The Beatles", 1970, ["pop","rock"], "When I find myself in times of trouble, Mother Mary comes to me", ["peaceful","piano","gospel","comforting","classic"], "Comforting, piano-led rock gospel with McCartney's warm voice and timeless reassurance."),
    ("Come Together", "The Beatles", 1969, ["rock","blues rock"], "Here come old flat-top", ["hypnotic","bluesy","mysterious","funky","classic"], "Hypnotic, bass-driven Beatles track with cryptic lyrics and an unmistakable groove."),
    ("Yesterday", "The Beatles", 1965, ["pop","acoustic"], "Yesterday, all my troubles seemed so far away", ["melancholic","nostalgic","acoustic","string","classic"], "Timeless string-quartet ballad of regret—one of the most covered songs ever written."),
    ("Bohemian Rhapsody", "Queen", 1975, ["rock","progressive"], "Is this the real life? Is this just fantasy?", ["epic","operatic","dramatic","theatrical","shifting"], "Multi-part rock epic that shifts from ballad to operatic pastiche to hard-rock fury."),
    ("We Will Rock You", "Queen", 1977, ["rock","hard rock"], "Buddy you're a boy make a big noise", ["anthemic","stomp","singalong","minimalist","energetic"], "Primal stomp-and-clap anthem stripped to its rhythmic bare bones for maximum crowd impact."),
    ("We Are the Champions", "Queen", 1977, ["rock"], "I've paid my dues, time after time", ["triumphant","anthemic","uplifting","singalong","stadium"], "Triumphant stadium anthem celebrating perseverance—a universal victory song."),
    ("Don't Stop Me Now", "Queen", 1978, ["rock","pop"], "Tonight I'm gonna have myself a real good time", ["euphoric","fun","upbeat","energetic","joyful"], "Euphoric, breathlessly fast rock song brimming with charismatic energy and joy."),
    ("Born to Run", "Bruce Springsteen", 1975, ["rock","heartland rock"], "In the day we sweat it out on the streets of a runway American dream", ["epic","driving","anthemic","yearning","American"], "Epic Springsteen anthem of youth, escape, and the open highway."),
    ("Thunder Road", "Bruce Springsteen", 1975, ["rock","heartland rock"], "The screen door slams, Mary's dress waves", ["romantic","storytelling","anthemic","piano","American"], "Heartland rock masterpiece that opens with a lone harmonica and tells a vivid escape narrative."),
    ("American Pie", "Don McLean", 1971, ["folk","rock"], "A long, long time ago I can still remember", ["nostalgic","epic","folk","storytelling","bittersweet"], "8-minute folk-rock epic lamenting the death of the 50s innocence through cryptic symbolism."),
    ("More Than a Feeling", "Boston", 1976, ["rock"], "I looked out this morning and the sun was gone", ["melodic","anthemic","guitar","nostalgic","classic-rock"], "Melodic hard-rock with layered acoustic and electric guitars and soaring harmonies."),
    ("Eye of the Tiger", "Survivor", 1982, ["rock"], "Risin' up, back on the street", ["motivating","anthemic","driving","80s","iconic"], "Iconic motivational rock anthem with a propulsive, punchy guitar riff."),
    ("Jump", "Van Halen", 1984, ["rock","pop"], "I ain't the worst that you've seen", ["energetic","upbeat","synth","fun","catchy"], "Irresistibly fun 80s rock driven by Eddie Van Halen's synthesizer riff."),
    ("Pour Some Sugar on Me", "Def Leppard", 1987, ["rock","glam metal"], "Love is like a bomb, baby", ["fun","energetic","glam","anthemic","80s"], "Massive 80s glam-metal anthem with a monster chorus and stadium-filling power."),
    ("Livin' on a Prayer", "Bon Jovi", 1986, ["rock","glam metal"], "Tommy used to work on the docks", ["anthemic","singalong","working-class","uplifting","80s"], "Blue-collar working-class rock anthem that soars into one of the decade's great choruses."),
    ("Wanted Dead or Alive", "Bon Jovi", 1986, ["rock","country rock"], "It's all the same, only the names will change", ["cinematic","lonesome","storytelling","guitar","acoustic"], "Cinematic rock ballad with an acoustic guitar opening and romantic roadhouse imagery."),
    # ── ROCK – ALTERNATIVE / INDIE ────────────────────────────────────────────
    ("Creep", "Radiohead", 1992, ["alternative","rock"], "When you were here before, couldn't look you in the eye", ["melancholic","raw","angsty","quiet-loud","self-loathing"], "Quiet-loud grunge-pop with crushing self-loathing and a famous explosive guitar break."),
    ("Karma Police", "Radiohead", 1997, ["alternative","rock"], "Karma police, arrest this man", ["atmospheric","haunting","piano","unsettling","indie"], "Atmospheric piano-driven Radiohead track with an unsettling, accusatory tone."),
    ("Fake Plastic Trees", "Radiohead", 1995, ["alternative","indie"], "Her green plastic watering can", ["melancholic","acoustic","sad","ethereal","gentle"], "Delicate, heartbreaking acoustic ballad about emotional emptiness in modern life."),
    ("Seven Nation Army", "The White Stripes", 2003, ["alternative","garage rock"], "I'm gonna fight 'em off", ["driving","riff-based","minimalist","anthemic","raw"], "Unstoppable garage-rock riff on a baritone guitar—one of the most recognizable in rock."),
    ("Fell in Love with a Girl", "The White Stripes", 2002, ["alternative","garage rock"], "Fell in love with a girl", ["raw","energetic","garage","fast","minimal"], "Blistering, 2-minute garage rock explosion with no-frills energy and charm."),
    ("Mr. Brightside", "The Killers", 2003, ["indie rock","alternative"], "Coming out of my cage and I've been doing just fine", ["anxious","driving","indie","jealous","frenetic"], "Frenetic indie-rock about jealousy and obsession with a pulsing synth-rock energy."),
    ("Somebody Told Me", "The Killers", 2004, ["indie rock","synth-rock"], "Now somebody told me you had a boyfriend", ["danceable","energetic","synth-rock","indie","catchy"], "High-energy synth-rock with a playful, paranoid edge and danceable groove."),
    ("Yellow", "Coldplay", 2000, ["alternative","pop"], "Look at the stars, look how they shine for you", ["romantic","gentle","melodic","acoustic","tender"], "Tender, gentle alternative-rock love song with sparkling guitar and understated emotion."),
    ("The Scientist", "Coldplay", 2002, ["alternative","pop"], "Come up to meet you, tell you I'm sorry", ["melancholic","piano","emotional","acoustic","sad"], "Slow, melancholic piano ballad of regret sung backwards in the famous music video."),
    ("Fix You", "Coldplay", 2005, ["alternative","pop"], "When you try your best but you don't succeed", ["uplifting","emotional","building","cathartic","hopeful"], "Emotional anthem that builds from sparse piano to a cathartic, uplifting final chorus."),
    ("Clocks", "Coldplay", 2002, ["alternative","pop"], "The lights go out and I can't be saved", ["driving","piano","urgent","anthemic","melodic"], "Urgent, looping piano riff propels this landmark Coldplay track to stadium-filling heights."),
    ("Use Somebody", "Kings of Leon", 2008, ["alternative","rock"], "I've been roaming around, always looking down", ["anthemic","emotional","raw","stadium","longing"], "Raw, soaring alternative-rock anthem of longing for human connection."),
    ("Sex on Fire", "Kings of Leon", 2008, ["alternative","rock"], "You, your sex is on fire", ["driving","raw","catchy","anthemic","energetic"], "Pulsing, raw rock with a memorable falsetto hook and barely contained energy."),
    ("Float On", "Modest Mouse", 2004, ["indie rock","alternative"], "I backed my car into a cop car the other day", ["optimistic","quirky","indie","driving","lo-fi"], "Quirky, surprisingly optimistic indie-rock about rolling with life's mishaps."),
    ("Such Great Heights", "The Postal Service", 2003, ["indie pop","electronic"], "I am thinking it's a sign that the freckles in our eyes are mirror images", ["electronic","romantic","indie","twee","melodic"], "Warm, melodic electronica-pop love song with stuttering beats and heartfelt lyrics."),
    ("Ho Hey", "The Lumineers", 2012, ["folk","indie"], "I've been trying to do it right", ["folk","upbeat","acoustic","singalong","romantic"], "Stomping folk-pop with simple acoustic joy and a beloved singalong chorus."),
    ("Stubborn Love", "The Lumineers", 2012, ["folk","indie"], "Keep your head up, keep your love", ["acoustic","uplifting","folk","tender","sincere"], "Tender folk-rock about persevering in love with gentle acoustic warmth."),
    ("Pumped Up Kicks", "Foster the People", 2010, ["indie pop","alternative"], "All the other kids with the pumped up kicks", ["catchy","dark","whistling","indie","deceptive"], "Deceptively catchy indie-pop with a dark subject masked by an irresistibly danceable groove."),
    ("Dog Days Are Over", "Florence + The Machine", 2009, ["indie pop","alternative"], "Happiness hit her like a train on a track", ["euphoric","building","powerful","unique","energetic"], "Building, euphoric indie-pop anthem with harp, percussion and Florence's soaring voice."),
    ("Shake It Out", "Florence + The Machine", 2011, ["indie pop","alternative"], "Regrets collect like old friends", ["cathartic","gospel","powerful","emotional","uplifting"], "Gospel-influenced indie-pop with a cathartic, arms-raised emotional release."),
    ("Skinny Love", "Bon Iver", 2008, ["indie folk","folk"], "Come on skinny love, just last the year", ["raw","heartbroken","folk","fragile","acoustic"], "Raw, fragile folk song recorded alone in a snow-covered Wisconsin cabin."),
    ("Holocene", "Bon Iver", 2011, ["indie folk","ambient"], "Somday my pain will mark you", ["ethereal","atmospheric","introspective","beautiful","indie"], "Shimmering, otherworldly indie-folk with majestic imagery and hushed emotional depth."),
    ("Stolen Dance", "Milky Chance", 2013, ["indie pop","folk"], "I want you by my side", ["breezy","acoustic","danceable","relaxed","summer"], "Breezy indie-folk with a downtempo, slightly hip-hop-influenced groove."),
    ("Little Talks", "Of Monsters and Men", 2011, ["indie folk","indie rock"], "I don't like walking around this old and empty house", ["anthemic","folk","duet","haunting","energetic"], "Energetic folk-rock duet with call-and-response vocals and a swelling, anthemic chorus."),
    ("Tongue Tied", "Grouplove", 2011, ["indie rock","alternative"], "Take me to your best friend's house", ["fun","energetic","carefree","indie","nostalgic"], "Fun, carefree indie-rock with a joyful burst of energy and nostalgic summer feeling."),
    ("Tenerife Sea", "Ed Sheeran", 2014, ["pop","acoustic"], "You look so wonderful in your dress", ["romantic","acoustic","tender","intimate","beautiful"], "Beautifully intimate acoustic love song with lush string arrangement."),
    ("Vienna", "Billy Joel", 1977, ["pop","rock"], "Slow down, you crazy child", ["philosophical","piano","nostalgic","wise","gentle"], "Gentle piano ballad about slowing down in youth—one of Billy Joel's most philosophical songs."),
    ("Piano Man", "Billy Joel", 1973, ["pop","rock"], "It's nine o'clock on a Saturday", ["storytelling","piano","nostalgic","bar","classic"], "Classic piano-bar storytelling song painting vivid portraits of working-class dreamers."),
    # ── HIP-HOP / RAP ─────────────────────────────────────────────────────────
    ("Lose Yourself", "Eminem", 2002, ["hip-hop","rap"], "Look, if you had one shot, or one opportunity", ["intense","motivational","driving","rap","cinematic"], "Urgent, driving rap anthem about seizing the moment—from the 8 Mile film."),
    ("Rap God", "Eminem", 2013, ["hip-hop","rap"], "", ["technical","fast","aggressive","lyrical","relentless"], "Dizzying technical showcase with Eminem delivering some of the fastest rapping ever recorded."),
    ("Stan", "Eminem", 2000, ["hip-hop","rap"], "My tea's gone cold, I'm wondering why I got out of bed at all", ["dark","storytelling","obsessive","emotional","narrative"], "Dark, disturbing narrative about an obsessive fan told through letters, with haunting Dido hook."),
    ("The Real Slim Shady", "Eminem", 2000, ["hip-hop","rap","pop"], "Will the real Slim Shady please stand up", ["provocative","satirical","fun","catchy","irreverent"], "Provocative, satirical rap with a catchy chorus skewering pop culture and celebrity."),
    ("Gold Digger", "Kanye West", 2005, ["hip-hop","R&B"], "She take my money when I'm in need", ["soulful","sample-heavy","humorous","catchy","groovy"], "Infectious soul-sample banger with Ray Charles flip and Jamie Foxx hook."),
    ("All Falls Down", "Kanye West", 2004, ["hip-hop","soul"], "Oh, when it all falls down", ["introspective","conscious","soulful","melodic","emotional"], "Soulful, introspective early Kanye about consumerism and insecurity."),
    ("Power", "Kanye West", 2010, ["hip-hop","soul"], "I'm livin' in that 21st century", ["epic","bombastic","orchestral","confident","dramatic"], "Orchestral hip-hop with king-sized ego, King Crimson sample, and cinematic scope."),
    ("Stronger", "Kanye West", 2007, ["hip-hop","electronic"], "That that don't kill me can only make me stronger", ["driving","electronic","Daft-Punk","confident","energetic"], "Hard-hitting rap built on Daft Punk's Harder Better Faster with robotic energy."),
    ("99 Problems", "Jay-Z", 2004, ["hip-hop","rock"], "If you're having girl problems, I feel bad for you son", ["aggressive","rock-influenced","confident","hard","swagger"], "Confrontational, rock-infused hip-hop with a Rick Rubin production and sharp wit."),
    ("Empire State of Mind", "Jay-Z ft. Alicia Keys", 2009, ["hip-hop","pop"], "In New York, concrete jungle where dreams are made of", ["anthemic","NYC","triumphant","cinematic","epic"], "Grand New York City anthem blending Jay-Z's boastful verse with Alicia Keys's soaring chorus."),
    ("Hotline Bling", "Drake", 2015, ["hip-hop","R&B","dancehall"], "You used to call me on my cell phone", ["moody","dancehall","melodic","catchy","R&B"], "Melodic, dancehall-tinged hip-hop with mellow production and possessive romantic tension."),
    ("God's Plan", "Drake", 2018, ["hip-hop","R&B"], "I been movin' calm, don't start no trouble with me", ["laid-back","melodic","smooth","rap","catchy"], "Smooth, melodic hip-hop with a generous spirit and effortlessly cool delivery."),
    ("HUMBLE.", "Kendrick Lamar", 2017, ["hip-hop","rap"], "Sit down, be humble", ["minimal","piano","hard","confident","punchy"], "Hard-hitting Kendrick single with a minimal piano loop, snapping drums, and commanding presence."),
    ("DNA.", "Kendrick Lamar", 2017, ["hip-hop","rap"], "I got, I got, I got, I got loyalty", ["aggressive","energetic","hard","complex","assertive"], "Intense, rapid-fire Kendrick track asserting Black excellence with cinematic production shifts."),
    ("Alright", "Kendrick Lamar", 2015, ["hip-hop","rap","soul"], "Alls my life I has to fight", ["uplifting","conscious","jazzy","emotional","protest"], "Jazzy, uplifting protest anthem that became a rallying cry for the Black Lives Matter movement."),
    ("Swimming Pools (Drank)", "Kendrick Lamar", 2012, ["hip-hop","rap"], "Pour up, drank, head shot, drank", ["hypnotic","dark","introspective","slow","moody"], "Hypnotic, double-time rap meditation on peer pressure and addiction over a stark beat."),
    ("Sicko Mode", "Travis Scott", 2018, ["hip-hop","trap"], "Sun is down, freezing cold", ["trap","hard","multi-part","dark","bass-heavy"], "Multi-part trap epic with dramatic beat switches and heavy 808 bass—a modern landmark."),
    ("Goosebumps", "Travis Scott", 2016, ["hip-hop","trap","psychedelic"], "Girl, you gimme that feeling", ["psychedelic","bass-heavy","moody","trap","hypnotic"], "Psychedelic trap with warped vocals, deep bass, and a distinctly nocturnal feel."),
    ("Mask Off", "Future", 2017, ["hip-hop","trap"], "Percocet, Molly, Percocet", ["hypnotic","flute","trap","dark","moody"], "Hypnotic trap built on a haunting flute loop—one of the signature sounds of late 2010s rap."),
    ("Bodak Yellow", "Cardi B", 2017, ["hip-hop","rap","trap"], "Said little bitch, you can't fuck with me", ["aggressive","confident","hard","trap","assertive"], "Assertive, hard-hitting trap debut that made Cardi B the first solo female rapper to top the charts since Lauryn Hill."),
    ("WAP", "Cardi B ft. Megan Thee Stallion", 2020, ["hip-hop","rap","trap"], "", ["explicit","bass-heavy","confident","trap","empowering"], "Unapologetically explicit female empowerment banger with hard-hitting bass production."),
    ("Savage", "Megan Thee Stallion", 2020, ["hip-hop","rap"], "Bad bitch, I know that I look good", ["confident","danceable","assertive","trap","catchy"], "Confident, bass-driven trap anthem celebrating self-assured Black femininity."),
    ("Rockstar", "Post Malone ft. 21 Savage", 2017, ["hip-hop","trap","rock"], "I've been fucking hoes and popping pillies", ["dark","moody","bass","melodic","rock-rap"], "Dark, melodic rap with rock-star imagery and a haunting production that topped charts for months."),
    ("Sunflower", "Post Malone & Swae Lee", 2018, ["hip-hop","pop","R&B"], "I thought you left me 'cause I wasn't enough", ["melodic","dreamy","smooth","catchy","pop-rap"], "Smooth, dreamy pop-rap crossover from the Spider-Man soundtrack with irresistible melody."),
    ("Circles", "Post Malone", 2019, ["pop","hip-hop"], "Run away, but we're running in circles", ["melancholic","melodic","pop","acoustic","sad"], "Melancholic pop song about a relationship stuck in a painful loop."),
    ("Old Town Road", "Lil Nas X", 2019, ["hip-hop","country"], "Yeah, I'm gonna take my horse to the old town road", ["fun","genre-bending","country-rap","catchy","viral"], "Genre-defying country-trap viral smash that broke chart records."),
    ("MONTERO (Call Me By Your Name)", "Lil Nas X", 2021, ["pop","hip-hop"], "I caught it bad yesterday", ["provocative","camp","danceable","flamboyant","catchy"], "Provocative, camp pop-rap with biblical imagery and a glittery, danceable production."),
    ("This Is America", "Childish Gambino", 2018, ["hip-hop","funk","soul"], "We just wanna party, party just for you", ["political","jarring","satirical","funk","complex"], "Jarring, politically charged funk that contrasts carefree choreography with shocking violence."),
    ("Redbone", "Childish Gambino", 2016, ["R&B","funk","soul"], "Stay woke", ["psychedelic-soul","groovy","warm","sexy","funk"], "Warm, psychedelic soul with a deep groove inspired by 70s funk and a gentle warning."),
    ("Lucid Dreams", "Juice WRLD", 2018, ["hip-hop","pop","emo-rap"], "I still see your shadows in my room", ["emotional","melodic","sad","dark","emo-rap"], "Emo-rap built on an Sting sample, blending heartbreak and melodic hooks."),
    ("Robbery", "Juice WRLD", 2019, ["hip-hop","pop","emo-rap"], "She told me put my heart in a bag", ["heartbroken","melodic","trap","emotional","intimate"], "Confessional melodic trap about the emotional toll of a toxic relationship."),
    ("Rockstar", "DaBaby ft. Roddy Ricch", 2020, ["hip-hop","trap"], "Told my ex-bitch I'm a pop star", ["driving","confident","trap","catchy","aggressive"], "Hard-hitting protest rap turned pop anthem with a viral George Floyd reference verse."),
    ("Mood", "24kGoldn ft. iann dior", 2020, ["hip-hop","pop-punk"], "Why you always in a mood", ["catchy","pop-punk-rap","upbeat","energetic","crossover"], "Genre-blurring pop-punk rap crossover that dominated radio with energetic brevity."),
    ("Levitating", "Dua Lipa", 2020, ["pop","disco"], "I got you, moonlight", ["disco","danceable","euphoric","upbeat","catchy"], "Glittery disco-pop with cosmic imagery and an irresistible dancefloor-ready groove."),
    ("INDUSTRY BABY", "Lil Nas X ft. Jack Harlow", 2021, ["hip-hop","pop"], "Baby back, bitch", ["triumphant","brass","trap","confident","fun"], "Triumphant trap banger with blaring brass and an unapologetically confident attitude."),
    # ── R&B / SOUL ────────────────────────────────────────────────────────────
    ("Superstition", "Stevie Wonder", 1972, ["R&B","soul","funk"], "Very superstitious, writings on the wall", ["funky","iconic","groove","upbeat","clavinet"], "Classic funk-soul driven by Stevie's iconic clavinet groove and infectious energy."),
    ("Isn't She Lovely", "Stevie Wonder", 1976, ["R&B","soul"], "Isn't she lovely, made from love", ["joyful","harmonica","warm","celebratory","sweet"], "Joyful, harmonica-led celebration of his newborn daughter—pure musical happiness."),
    ("I Wish", "Stevie Wonder", 1976, ["R&B","funk","soul"], "Looking back on when I was a little nappy-headed boy", ["nostalgic","funky","warm","playful","danceable"], "Nostalgic, funky Stevie Wonder track celebrating childhood memories with irresistible groove."),
    ("Sir Duke", "Stevie Wonder", 1977, ["R&B","soul","jazz"], "Music is a world within itself", ["joyful","brass","upbeat","danceable","celebratory"], "Celebratory Stevie Wonder tribute to Duke Ellington with joyful brass and infectious swing."),
    ("What's Going On", "Marvin Gaye", 1971, ["R&B","soul"], "Mother, mother, there's too many of you crying", ["soulful","political","gentle","conscious","melancholic"], "Gentle, flowing soul protest about war and social injustice—a landmark of conscious R&B."),
    ("Let's Get It On", "Marvin Gaye", 1973, ["R&B","soul"], "I've been really trying, baby", ["sensual","smooth","romantic","intimate","classic"], "Smooth, sensual soul classic that epitomizes romantic intimacy and timeless seduction."),
    ("Sexual Healing", "Marvin Gaye", 1982, ["R&B","soul"], "Baby, I'm hot just like an oven", ["sensual","groove","drum-machine","smooth","iconic"], "Smooth, synthesizer-led R&B with a gentle drum machine and Marvin's irresistibly seductive vocal."),
    ("Respect", "Aretha Franklin", 1967, ["soul","R&B"], "What you want, baby I got", ["empowering","soulful","anthemic","feminist","classic"], "Soul masterpiece that became an anthem of civil rights and female empowerment."),
    ("Natural Woman", "Aretha Franklin", 1967, ["soul","R&B"], "Looking out on the morning rain", ["soulful","emotional","gospel","powerful","classic"], "Deeply soulful, gospel-inflected ballad about feeling complete in love."),
    ("I Will Always Love You", "Whitney Houston", 1992, ["R&B","pop","ballad"], "If I should stay, I would only be in your way", ["powerful","vocal","ballad","emotional","iconic"], "Breathtaking vocal showcase—Whitney's definitive moment, from The Bodyguard."),
    ("Greatest Love of All", "Whitney Houston", 1986, ["R&B","pop"], "I believe the children are the future", ["uplifting","empowering","gospel","ballad","soaring"], "Inspirational pop ballad with Whitney's gospel-rooted vocal power at its most uplifting."),
    ("I Wanna Dance with Somebody", "Whitney Houston", 1987, ["pop","R&B","dance"], "I need a man who'll take a chance on a love", ["upbeat","danceable","joyful","80s","feel-good"], "Joyful 80s dance-pop with Whitney's soaring vocals over a bouncy, irresistible beat."),
    ("No One", "Alicia Keys", 2007, ["R&B","soul"], "I just want you close, where you can stay forever", ["romantic","piano","soulful","warm","uplifting"], "Warm piano-soul love song with Alicia Keys's powerful, emotive voice."),
    ("Fallin'", "Alicia Keys", 2001, ["R&B","soul"], "I keep on fallin' in and out of love with you", ["emotional","piano","raw","soulful","debut"], "Raw, emotional debut single showcasing Alicia's piano mastery and soulful voice."),
    ("Empire State of Mind", "Alicia Keys", 2009, ["R&B","pop"], "In New York, concrete jungle where dreams are made of", ["anthemic","NYC","uplifting","powerful","chorus"], "Soaring New York City tribute that became the unofficial anthem of the city."),
    ("Say My Name", "Destiny's Child", 1999, ["R&B","pop"], "Say my name, say my name", ["suspicious","groove","catchy","90s-R&B","melodic"], "Smooth, suspicious R&B with interlocking harmonies and a memorable groove."),
    ("Crazy in Love", "Beyoncé", 2003, ["R&B","hip-hop","pop"], "Got me looking so crazy right now, your love's got me looking so crazy", ["energetic","iconic","brassy","danceable","hip-hop"], "Powerhouse R&B-pop with a horn sample, hip-hop groove, and unstoppable energy."),
    ("Lemonade (Hold Up)", "Beyoncé", 2016, ["R&B","pop","reggae"], "I ain't sorry, no I ain't sorry", ["defiant","joyful","reggae","empowering","carefree"], "Reggae-infused R&B with a carefree, defiant energy masking deep emotional pain."),
    ("Formation", "Beyoncé", 2016, ["R&B","hip-hop","trap"], "Ok ladies now let's get in formation", ["powerful","political","Southern-hip-hop","bass-heavy","fierce"], "Fierce, politically charged anthem celebrating Black Southern identity with trap production."),
    ("XO", "Beyoncé", 2013, ["pop","R&B"], "In the darkest night hour I searched through the crowd", ["romantic","upbeat","anthemic","carefree","stadium"], "Upbeat romantic stadium-pop with carefree exuberance and a powerful singalong chorus."),
    ("Stay With Me", "Sam Smith", 2014, ["R&B","soul","pop"], "Guess it's true, I'm not good at a one-night stand", ["emotional","gospel","soulful","pleading","honest"], "Raw, emotionally honest gospel-soul ballad pleading for company after a one-night stand."),
    ("Writing's on the Wall", "Sam Smith", 2015, ["R&B","pop","soul"], "I've been here before, but always hit the floor", ["dramatic","ballad","emotional","cinematic","Bond"], "Cinematic Bond theme with sweeping strings and Sam Smith's soaring falsetto."),
    ("Earned It", "The Weeknd", 2015, ["R&B","pop"], "You make it look like it's magic", ["smooth","cinematic","seductive","orchestral","R&B"], "Smooth orchestral R&B from Fifty Shades of Grey with seductive sophistication."),
    ("Can't Feel My Face", "The Weeknd", 2015, ["pop","R&B"], "And I know she'll be the death of me", ["upbeat","Motown-inspired","catchy","danceable","slick"], "Deceptively upbeat Motown-influenced pop masking dark subject matter with shiny production."),
    ("Often", "The Weeknd", 2014, ["R&B","electronic"], "She said she often stop, she always knockin' on wood", ["sensual","dark","electronic","nocturnal","smooth"], "Dark, sensual electronic R&B with hypnotic production and nocturnal atmosphere."),
    ("Adorn", "Miguel", 2012, ["R&B","soul"], "These lips can't wait to taste your skin, baby", ["sensual","soulful","smooth","modern-R&B","intimate"], "Sensual, neo-soul with silky modern production and heartfelt romantic devotion."),
    ("Redbone", "Childish Gambino", 2016, ["R&B","funk","soul"], "If you want it, you can have it", ["psychedelic","warm","funky","70s-soul","groove"], "70s-influenced psychedelic soul groove with Childish Gambino's impassioned falsetto."),
    ("Come Through and Chill", "Miguel", 2017, ["R&B","pop"], "Do the things that we used to do", ["smooth","mellow","late-night","R&B","romantic"], "Mellow, late-night R&B with hazy electronic production and a casual romantic invitation."),
    ("Location", "Khalid", 2016, ["R&B","pop"], "I don't need to know your name, I just wanna know your location", ["breezy","youthful","soulful","honest","relaxed"], "Breezy, youthful R&B debut with honest lyrics and a relaxed, warm production."),
    ("Young Dumb & Broke", "Khalid", 2017, ["R&B","pop"], "Young, dumb, broke high school kids", ["nostalgic","youthful","melodic","bittersweet","honest"], "Nostalgic, bittersweet teen anthem about carefree high-school days and young love."),
    ("ISPY", "KYLE ft. Lil Yachty", 2017, ["hip-hop","pop","R&B"], "I spy with my little eye", ["fun","catchy","carefree","light","summer"], "Light, fun summer rap-pop with an easygoing carefree energy."),
    ("Issues", "Julia Michaels", 2017, ["pop","R&B"], "I got issues, you got 'em too", ["honest","confessional","catchy","indie-pop","self-aware"], "Disarmingly honest confessional pop about mutual dysfunction in a relationship."),
    # ── ELECTRONIC / DANCE ────────────────────────────────────────────────────
    ("One More Time", "Daft Punk", 2000, ["electronic","house","dance"], "One more time, we're gonna celebrate", ["euphoric","house","uplifting","vocal","classic"], "Euphoric French house classic with a pitched-up vocal and endless feel-good energy."),
    ("Around the World", "Daft Punk", 1997, ["electronic","house","techno"], "Around the world, around the world", ["hypnotic","repetitive","robotic","house","iconic"], "Hypnotic, minimalist electronic house built on a single repeated phrase—pure groove."),
    ("Harder Better Faster Stronger", "Daft Punk", 2001, ["electronic","house","funk"], "Work it harder, make it better", ["robotic","driving","funk","iconic","chopped"], "Chopped vocal funk-house with robot voices and relentless upward energy."),
    ("Levels", "Avicii", 2011, ["electronic","EDM","progressive house"], "Oh, sometimes I get a good feeling", ["euphoric","anthemic","EDM","uplifting","drop"], "Festival-defining progressive house with a soaring Etta James sample and euphoric drop."),
    ("Wake Me Up", "Avicii", 2013, ["electronic","folk","pop","EDM"], "Feeling my way through the darkness", ["uplifting","folk-EDM","emotional","crossover","acoustic"], "Genre-blending folk-EDM crossover with an acoustic guitar intro and festival-ready drop."),
    ("Animals", "Martin Garrix", 2013, ["electronic","EDM","progressive house"], "", ["energetic","drop","festival","driving","hard"], "Driving progressive house anthem built on an enormous, aggressive festival drop."),
    ("Titanium", "David Guetta ft. Sia", 2011, ["electronic","EDM","pop"], "You shout it loud but I can't hear a word you say", ["powerful","anthemic","EDM","uplifting","Sia"], "Powerful anthemic EDM with Sia's soaring, resilient vocal over a pulsing house beat."),
    ("Don't You Worry Child", "Swedish House Mafia", 2012, ["electronic","progressive house","EDM"], "There was a time I used to look into my father's eyes", ["nostalgic","anthemic","uplifting","EDM","emotional"], "Anthemic farewell progressive house with nostalgic lyrics and a soaring drop."),
    ("Clarity", "Zedd ft. Foxes", 2012, ["electronic","pop","EDM"], "I drink from the river, no I drink from the rain", ["emotional","powerful","EDM","anthemic","pop"], "Powerful electro-pop anthem with an emotionally charged vocal and euphoric synth drop."),
    ("Roses", "SAINt JHN (Imanbek Remix)", 2019, ["electronic","dance","pop"], "I could take the tears I've cried for you", ["viral","danceable","melodic","upbeat","trap-house"], "Infectious melodic remix that became a global viral sensation with an irresistible swing."),
    ("Strobe", "deadmau5", 2009, ["electronic","progressive house"], "", ["atmospheric","building","ethereal","epic","hypnotic"], "Epic, slowly building 10-minute progressive house piece that feels like a journey through space."),
    ("Scary Monsters and Nice Sprites", "Skrillex", 2010, ["electronic","dubstep","EDM"], "", ["aggressive","heavy","drop","iconic","bass-heavy"], "Iconic dubstep track that introduced the genre's signature wobble bass to the mainstream."),
    ("Cinema", "Skrillex & Benny Benassi", 2011, ["electronic","dubstep","EDM"], "You are the cinema I see my future in", ["emotional","dubstep","pop","anthemic","uplifting"], "Anthemic dubstep-pop with an emotional Benny Benassi track transformed by Skrillex's energy."),
    ("Lean On", "Major Lazer ft. MØ", 2015, ["electronic","dancehall","pop"], "Blow a kiss, fire a gun", ["dancehall","upbeat","global","catchy","uplifting"], "Global megahit blending dancehall rhythms with infectious pop hooks."),
    ("Cold Water", "Major Lazer ft. Justin Bieber & MØ", 2016, ["electronic","pop","tropical"], "Everybody gets high, everybody gets low", ["uplifting","tropical","emotional","pop","summer"], "Uplifting tropical-pop about perseverance through hardship with Bieber's smooth vocal."),
    ("The Middle", "Zedd, Maren Morris & Grey", 2018, ["pop","dance","country"], "Why won't you meet me in the middle", ["catchy","upbeat","pop","danceable","crossover"], "Genre-crossing pop-dance anthem with a massive, accessible chorus."),
    ("Memories", "Maroon 5", 2019, ["pop","acoustic"], "Here's to the ones that we got", ["nostalgic","acoustic","bittersweet","piano","singalong"], "Simple, nostalgic acoustic piano ballad celebrating memories of those we've lost."),
    ("Moves Like Jagger", "Maroon 5 ft. Christina Aguilera", 2011, ["pop","rock","dance"], "I've got the moves like Jagger", ["fun","catchy","slick","confident","groove"], "Slick, confident pop-rock with a swaggering groove and a surprising harmonica hook."),
    ("This Love", "Maroon 5", 2004, ["pop","rock"], "I was so high I did not recognize the fire burning in her eyes", ["passionate","rock","catchy","emotional","guitar"], "Passionate pop-rock with intertwining guitar lines and emotional intensity."),
    ("Animals", "Maroon 5", 2014, ["pop","R&B"], "Baby, I'm preying on you tonight", ["dark","sensual","driving","catchy","controversial"], "Dark, driving pop-R&B with hunting metaphors and a swaggering, pulsing production."),
    ("Waves", "Mr. Probz", 2013, ["pop","R&B","electronic"], "I'm slowly drifting away", ["mellow","smooth","reflective","melancholic","electronic"], "Mellow, smooth electronic-pop with a gently flowing rhythm and reflective tone."),
    ("Hymn for the Weekend", "Coldplay ft. Beyoncé", 2016, ["pop","electronic"], "Drink from me, drink from me", ["uplifting","colorful","Bollywood-inspired","joyful","spiritual"], "Vibrant, uplifting pop with Bollywood-influenced production and celebratory energy."),
    ("Something Just Like This", "The Chainsmokers & Coldplay", 2017, ["pop","EDM"], "I've been reading books of old, the legends and the myths", ["uplifting","melodic","EDM","romantic","anthemic"], "Uplifting EDM-pop crossover with an understated romantic lyric and soaring chorus."),
    ("Closer", "The Chainsmokers ft. Halsey", 2016, ["pop","EDM"], "Hey, I was doing just fine before I met you", ["nostalgic","catchy","pop","indie","emotional"], "Nostalgic, catchy indie-influenced EDM-pop with a relatable story of running into an ex."),
    # ── JAZZ (ADDITIONAL) ─────────────────────────────────────────────────────
    ("Fly Me to the Moon", "Frank Sinatra", 1964, ["jazz","vocal jazz","standards"], "Fly me to the moon, let me play among the stars", ["romantic","smooth","swing","classic","timeless"], "Timeless jazz standard with Sinatra's effortless swing and romantic sentiment."),
    ("The Girl from Ipanema", "Stan Getz & João Gilberto", 1964, ["jazz","bossa nova"], "Tall and tan and young and lovely", ["breezy","bossa nova","romantic","cool","Brazilian"], "The definitive bossa nova track—languid, romantic, and effortlessly cool."),
    ("What a Wonderful World", "Louis Armstrong", 1968, ["jazz","pop"], "I see trees of green, red roses too", ["optimistic","warm","nostalgic","gentle","uplifting"], "Gentle jazz standard with Louis Armstrong's gravelly voice celebrating life's simple beauty."),
    ("Summertime", "Ella Fitzgerald & Louis Armstrong", 1957, ["jazz","blues","standards"], "Summertime, and the livin' is easy", ["dreamy","sultry","blues","slow","soulful"], "Dreamy, sultry Gershwin standard rendered with warm jazz feeling."),
    ("Round Midnight", "Thelonious Monk", 1947, ["jazz","bebop"], "", ["dark","moody","complex","bebop","introspective"], "Moody, harmonically complex bebop ballad that became one of jazz's most covered compositions."),
    ("My Favorite Things", "John Coltrane", 1960, ["jazz","modal"], "Raindrops on roses and whiskers on kittens", ["joyful","modal","inventive","swinging","spiritual"], "Coltrane's radical reimagining of a Broadway tune as a modal jazz exploration."),
    ("A Love Supreme, Pt. I", "John Coltrane", 1965, ["jazz","modal","spiritual"], "", ["spiritual","intense","searching","complex","devotional"], "Opening section of Coltrane's devotional masterpiece—meditative, intense, spiritually searching."),
    ("Autumn Leaves", "Miles Davis", 1958, ["jazz","standards","bebop"], "The falling leaves drift by my window", ["melancholic","smooth","standard","bittersweet","cool"], "Beautifully melancholic standard played with Miles Davis's trademark cool restraint."),
    ("All Blues", "Miles Davis", 1959, ["jazz","modal"], "", ["cool","modal","relaxed","bluesy","hypnotic"], "Hypnotic modal jazz in 6/4 with Miles Davis's muted trumpet and a gently swinging blues feel."),
    ("Chameleon", "Herbie Hancock", 1973, ["jazz","funk","jazz-funk"], "", ["funky","groove","bass-heavy","jazz-funk","danceable"], "Deep, bass-driven jazz-funk groove that bridged jazz and 70s funk culture."),
    ("Watermelon Man", "Herbie Hancock", 1962, ["jazz","funk","hard bop"], "", ["funky","energetic","hard-bop","groove","joyful"], "Energetic hard-bop funk with an irresistible groove that became a jazz standard."),
    ("Maiden Voyage", "Herbie Hancock", 1965, ["jazz","modal","post-bop"], "", ["ethereal","oceanic","modal","dreamy","abstract"], "Ethereal, oceanic modal jazz evoking the feeling of being adrift at sea."),
    ("Birdland", "Weather Report", 1977, ["jazz","jazz-fusion"], "", ["driving","energetic","jazz-fusion","electric","virtuosic"], "Electric, virtuosic jazz-fusion celebrating the famous NYC jazz club."),
    ("Spain", "Chick Corea", 1972, ["jazz","jazz-fusion","flamenco"], "", ["virtuosic","flamenco-jazz","joyful","complex","driving"], "Joyful, flamenco-influenced jazz-fusion masterpiece with dazzling virtuosity."),
    ("Cantaloupe Island", "Herbie Hancock", 1964, ["jazz","hard bop","acid jazz"], "", ["cool","groovy","hip-hop-sampled","laid-back","classic"], "Laid-back, funky hard-bop that was famously sampled in hip-hop and defined acid jazz."),
    ("Caravan", "Duke Ellington", 1937, ["jazz","big band","swing"], "", ["exotic","big-band","swinging","energetic","classic"], "Exotic, swinging big-band jazz classic with a distinctive tom-tom rhythm."),
    ("Take the A Train", "Duke Ellington", 1941, ["jazz","big band","swing"], "", ["upbeat","swinging","classic","bright","big-band"], "Bright, swinging big-band jazz—the signature theme song of Duke Ellington's orchestra."),
    ("So What", "Miles Davis", 1959, ["jazz","modal"], "", ["cool","modal","relaxed","spacious","improvised"], "Cool, spacious modal jazz built on two chords with a laid-back, exploratory feel."),
    # ── CLASSICAL (ADDITIONAL) ────────────────────────────────────────────────
    ("Moonlight Sonata (1st mvt)", "Ludwig van Beethoven", 1801, ["classical","piano","sonata"], "", ["melancholic","nocturnal","gentle","introspective","iconic"], "Hauntingly beautiful piano sonata with a gentle, rolling triplet accompaniment evoking moonlight."),
    ("Für Elise", "Ludwig van Beethoven", 1810, ["classical","piano"], "", ["delicate","iconic","melodic","wistful","piano"], "Delicate, instantly recognizable piano bagatelle—one of the most beloved pieces in classical music."),
    ("Toccata and Fugue in D minor", "Johann Sebastian Bach", 1703, ["classical","baroque","organ"], "", ["dramatic","powerful","dark","iconic","organ"], "Dramatic, thunderous organ masterpiece—among the most recognizable pieces in classical music."),
    ("Air on the G String", "Johann Sebastian Bach", 1717, ["classical","baroque","orchestral"], "", ["serene","elegant","peaceful","beautiful","slow"], "Serene, achingly beautiful baroque piece for strings—pure elegance and grace."),
    ("Brandenburg Concerto No. 3", "Johann Sebastian Bach", 1721, ["classical","baroque","concerto"], "", ["energetic","bright","baroque","complex","elegant"], "Energetic baroque concerto with interweaving string parts full of contrapuntal brilliance."),
    ("Bolero", "Maurice Ravel", 1928, ["classical","orchestral","modern"], "", ["hypnotic","building","repetitive","crescendo","Spanish"], "Hypnotic orchestral crescendo built on a single repeating Spanish dance theme—15 minutes of relentless build."),
    ("Rhapsody in Blue", "George Gershwin", 1924, ["classical","jazz","orchestral"], "", ["jazz-classical","sweeping","American","innovative","lush"], "Sweeping jazz-classical fusion capturing the energy and complexity of American life."),
    ("1812 Overture", "Pyotr Ilyich Tchaikovsky", 1882, ["classical","orchestral","romantic"], "", ["dramatic","bombastic","cannon","triumphant","epic"], "Bombastic orchestral epic celebrating Russia's victory over Napoleon—complete with cannon fire."),
    ("Swan Lake (Main Theme)", "Pyotr Ilyich Tchaikovsky", 1877, ["classical","ballet","romantic"], "", ["beautiful","romantic","tragic","graceful","elegant"], "Achingly romantic ballet theme full of tragic beauty and graceful melodic sweep."),
    ("Romeo and Juliet Fantasy Overture", "Pyotr Ilyich Tchaikovsky", 1870, ["classical","orchestral","romantic"], "", ["romantic","dramatic","tragic","lush","cinematic"], "Lush romantic orchestral narrative depicting Shakespeare's doomed love affair."),
    ("Nutcracker Suite – Dance of the Sugar Plum Fairy", "Pyotr Ilyich Tchaikovsky", 1892, ["classical","ballet","romantic"], "", ["magical","delicate","ethereal","holiday","celesta"], "Magical, delicate celesta-driven ballet miniature—quintessential holiday classical music."),
    ("In the Hall of the Mountain King", "Edvard Grieg", 1876, ["classical","romantic","orchestral"], "", ["creepy","building","exciting","playful","dark"], "Mischievously creepy orchestral piece that accelerates from sneaky quiet to wild chaos."),
    ("O Fortuna (Carmina Burana)", "Carl Orff", 1937, ["classical","choral","modern"], "O Fortuna, velut luna", ["dramatic","epic","choral","powerful","cinematic"], "Thunderously dramatic choral opening used in countless films—overwhelming orchestral power."),
    ("Hallelujah Chorus", "George Frideric Handel", 1741, ["classical","baroque","choral"], "Hallelujah!", ["triumphant","choral","uplifting","sacred","majestic"], "Magnificent, triumphant baroque choral piece that audiences traditionally stand for."),
    ("Messiah – He Shall Feed His Flock", "George Frideric Handel", 1741, ["classical","baroque","choral"], "", ["serene","sacred","gentle","spiritual","warm"], "Gentle, serene pastoral aria from Handel's Messiah with comforting spiritual warmth."),
    ("The Planets – Mars", "Gustav Holst", 1916, ["classical","orchestral","modern"], "", ["dark","ominous","driving","war","powerful"], "Dark, ominous orchestral portrait of the god of war—a 5/4 juggernaut of tension."),
    ("Rite of Spring (Opening)", "Igor Stravinsky", 1913, ["classical","modern","ballet"], "", ["dissonant","revolutionary","primal","complex","jarring"], "Revolutionary, dissonant ballet opening that caused a riot at its premiere—raw primal energy."),
    ("Pictures at an Exhibition – Promenade", "Modest Mussorgsky", 1874, ["classical","romantic","piano"], "", ["majestic","brass","colorful","walking","regal"], "Majestic opening brass fanfare representing a stroll through an art gallery."),
    ("The Four Seasons – Winter (1st mvt)", "Antonio Vivaldi", 1725, ["classical","baroque","concerto"], "", ["icy","dramatic","intense","violin","shivering"], "Icy, intense baroque violin concerto depicting the bite and struggle of winter."),
    ("Clarinet Concerto in A major (2nd mvt)", "Wolfgang Amadeus Mozart", 1791, ["classical","classical-period","concerto"], "", ["tender","melancholic","graceful","clarinet","poignant"], "Achingly tender clarinet movement—one of Mozart's most poignant and beloved pieces."),
    ("Dies Irae", "Guiseppe Verdi", 1874, ["classical","choral","romantic"], "Dies irae, dies illa", ["terrifying","dramatic","powerful","choral","epic"], "Terrifying choral Requiem movement depicting the Day of Wrath with crushing dramatic force."),
    # ── COUNTRY ───────────────────────────────────────────────────────────────
    ("Ring of Fire", "Johnny Cash", 1963, ["country","rockabilly"], "Love is a burning thing", ["iconic","driving","mariachi","storytelling","twangy"], "Iconic country classic with mariachi horns and a vivid metaphor for all-consuming love."),
    ("Folsom Prison Blues", "Johnny Cash", 1955, ["country","rockabilly"], "I hear the train a comin', it's rolling round the bend", ["dark","twangy","storytelling","raw","classic"], "Raw, twangy country narrative from a man watching trains from behind prison walls."),
    ("Jolene", "Dolly Parton", 1973, ["country"], "Jolene, Jolene, Jolene, Jolene", ["pleading","emotional","iconic","country","storytelling"], "Iconic, desperately pleading country ballad begging a flame-haired rival to leave her man alone."),
    ("9 to 5", "Dolly Parton", 1980, ["country","pop"], "Tumble outta bed and I stumble to the kitchen", ["fun","upbeat","working-class","catchy","feminist"], "Upbeat, fun working-class anthem about office drudgery that became a feminist touchstone."),
    ("Friends in Low Places", "Garth Brooks", 1990, ["country"], "Blame it all on my roots, I showed up in boots", ["fun","sing-along","rowdy","relatable","classic"], "Rowdy, sing-along country anthem about showing up uninvited at your ex's fancy party."),
    ("The Dance", "Garth Brooks", 1989, ["country"], "I could have missed the pain but I'd have had to miss the dance", ["emotional","bittersweet","romantic","classic","storytelling"], "Poignant country ballad about accepting heartbreak as the price of loving deeply."),
    ("Take Me Home, Country Roads", "John Denver", 1971, ["country","folk"], "Almost heaven, West Virginia", ["nostalgic","uplifting","acoustic","American","singalong"], "Warm, nostalgic folk-country celebrating West Virginia's natural beauty and a longing for home."),
    ("Rocky Mountain High", "John Denver", 1972, ["country","folk"], "He was born in the summer of his 27th year", ["peaceful","nature","acoustic","uplifting","serene"], "Serene acoustic meditation on finding spiritual peace in the Colorado mountains."),
    ("Tennessee Whiskey", "Chris Stapleton", 2015, ["country","soul"], "Used to spend my nights out in a barroom", ["soulful","slow","romantic","raw","gospel"], "Slow-burning soul-country ballad with Stapleton's raw, gospel-drenched voice."),
    ("Broken Halos", "Chris Stapleton", 2017, ["country","soul"], "Seen my share of broken halos, folded wings that used to fly", ["melancholic","soulful","acoustic","spiritual","emotional"], "Mournful, soulful country ballad about lost loved ones with gospel warmth."),
    ("Need You Now", "Lady A", 2009, ["country","pop"], "It's a quarter after one, I'm all alone and I need you now", ["romantic","emotional","midnight","duet","catchy"], "Late-night longing duet with emotional urgency and a polished country-pop sheen."),
    ("Before He Cheats", "Carrie Underwood", 2006, ["country","pop"], "Right now he's probably slow dancing with a bleach blonde tramp", ["angry","empowering","catchy","revenge","attitude"], "Catchy country-pop revenge anthem with memorably vivid imagery of car vandalism."),
    ("Jesus Take the Wheel", "Carrie Underwood", 2005, ["country","gospel"], "She was driving last Friday on her way to Cincinnati", ["spiritual","emotional","gospel","ballad","uplifting"], "Emotional country ballad with a spiritual message and Carrie's powerful vocal debut."),
    ("Body Like a Back Road", "Sam Hunt", 2017, ["country","pop"], "Body like a back road, driving with my eyes closed", ["breezy","summer","romantic","melodic","groove"], "Breezy, melodic country-pop with a groove-driven rhythm and sun-baked romantic imagery."),
    ("Wagon Wheel", "Darius Rucker", 2013, ["country","folk"], "Headed down south to the land of the pines", ["feel-good","singalong","acoustic","road-trip","nostalgic"], "Feel-good country folk singalong about a hitchhiking journey to see a beloved."),
    ("Something in the Water", "Carrie Underwood", 2014, ["country","gospel"], "He said 'I've been where you've been before'", ["uplifting","gospel","spiritual","emotional","baptism"], "Uplifting gospel-country celebrating a spiritual rebirth and the power of faith."),
    # ── LATIN ─────────────────────────────────────────────────────────────────
    ("Despacito", "Luis Fonsi ft. Daddy Yankee", 2017, ["reggaeton","Latin pop"], "Despacito, quiero respirar tu cuello despacito", ["sensual","danceable","Latin","catchy","tropical"], "Global reggaeton phenomenon with a smooth Latin groove and sensual tropical atmosphere."),
    ("Hips Don't Lie", "Shakira ft. Wyclef Jean", 2006, ["Latin pop","dance"], "I never really knew that she could dance like this", ["danceable","energetic","Latin","upbeat","fun"], "Energetic Latin dance-pop with irresistible rhythm and Shakira's distinctive hip-shaking delivery."),
    ("Waka Waka (This Time for Africa)", "Shakira", 2010, ["pop","African","Latin"], "You're a good soldier, choosing your battles", ["uplifting","energetic","anthemic","African","danceable"], "Uplifting World Cup anthem blending Colombian and African rhythms into a global celebration."),
    ("La Bamba", "Ritchie Valens", 1958, ["rock","Latin","folk"], "Para bailar la bamba, se necesita una poca de gracia", ["fun","upbeat","rockabilly","Mexican-folk","energetic"], "Energetic rock arrangement of a traditional Mexican folk song—a landmark of Latin rock."),
    ("Livin' la Vida Loca", "Ricky Martin", 1999, ["Latin pop","dance","rock"], "She's into superstitions, black cats and voodoo dolls", ["fun","energetic","danceable","Latin","catchy"], "Explosive Latin-rock crossover that brought reggaeton rhythms to a global pop audience."),
    ("Smooth", "Santana ft. Rob Thomas", 1999, ["rock","Latin","R&B"], "Man, it's a hot one", ["groove","Latin-rock","sensual","guitar","summer"], "Warm, sensual Latin-rock groove with Santana's signature guitar and a memorable hook."),
    ("Bailando", "Enrique Iglesias ft. Sean Paul", 2014, ["reggaeton","Latin pop"], "Tú me miras y me lleva la corriente", ["romantic","danceable","Latin","upbeat","fun"], "Infectious Latin pop with reggaeton rhythms and bilingual romance."),
    ("Shape of My Heart", "Sting", 1993, ["pop","acoustic"], "He deals the cards as a meditation", ["acoustic","mysterious","introspective","melancholic","guitar"], "Mysterious, introspective acoustic ballad with delicate guitar arpeggios and philosophical lyrics."),
    ("Con Calma", "Daddy Yankee & Snow", 2019, ["reggaeton","Latin pop"], "Con calma", ["laid-back","danceable","reggaeton","catchy","fun"], "Cool, laid-back reggaeton with a breezy attitude and global dancefloor appeal."),
    ("Mi Gente", "J Balvin & Willy William", 2017, ["reggaeton","Latin","electronic"], "", ["danceable","high-energy","Latin","electronic","upbeat"], "High-energy Latin electronic banger that became a global dancefloor sensation."),
    ("Malamente", "Rosalía", 2017, ["flamenco","pop"], "", ["haunting","flamenco","dark","unique","Spanish"], "Haunting avant-garde flamenco with Rosalía's extraordinary vocal and sparse percussion."),
    ("Con Altura", "Rosalía ft. J Balvin", 2019, ["flamenco","reggaeton","pop"], "", ["cool","danceable","unique","Spanish","modern-flamenco"], "Genre-blending modern flamenco-pop-reggaeton fusion with effortless cool."),
    ("Boom Boom", "RedOne, Daddy Yankee & French Montana", 2016, ["Latin pop","dance","EDM"], "", ["danceable","upbeat","fun","energetic","catchy"], "High-energy Latin dance-pop built for summer parties and dancefloors."),
    ("Te Boté", "Nio García, Casper Mágico & Bad Bunny", 2018, ["reggaeton","trap","Latin"], "", ["hard","danceable","bass-heavy","Latin-trap","catchy"], "Dominant Latin trap banger that spent months at the top of Latin charts."),
    ("Taki Taki", "DJ Snake ft. Selena Gomez, Ozuna & Cardi B", 2018, ["Latin pop","EDM","reggaeton"], "", ["danceable","tropical","fun","multilingual","upbeat"], "Global multilingual party anthem blending EDM, reggaeton, and pop."),
    # ── K-POP ─────────────────────────────────────────────────────────────────
    ("Dynamite", "BTS", 2020, ["K-pop","pop","disco"], "Cause I, I, I'm in the stars tonight", ["upbeat","disco","fun","catchy","feel-good"], "Retro disco-pop debut in English—upbeat, glossy, and impossible to resist."),
    ("Butter", "BTS", 2021, ["K-pop","pop","disco"], "Smooth like butter, like a criminal undercover", ["smooth","upbeat","catchy","danceable","glossy"], "Slick, high-gloss pop brimming with charisma and effortlessly cool energy."),
    ("Boy With Luv", "BTS ft. Halsey", 2019, ["K-pop","pop","synth-pop"], "Hey, are you the answer to a guy like me", ["bright","sweet","synth-pop","fun","infectious"], "Bright, sweet synth-pop celebrating the simple joy of loving someone."),
    ("DNA", "BTS", 2017, ["K-pop","pop","EDM"], "처음 만난 우리가 꼭 연결된 것처럼", ["upbeat","EDM","experimental","energetic","catchy"], "Energetic K-pop with an unusual flute-whistling hook and bright production."),
    ("How You Like That", "BLACKPINK", 2020, ["K-pop","pop","hip-hop"], "Look at you now, look at you now", ["fierce","dramatic","bass-heavy","empowering","drop"], "Fierce, dramatic K-pop drop with powerful attitude and commanding rap-pop energy."),
    ("Kill This Love", "BLACKPINK", 2019, ["K-pop","pop"], "I had to kill this love, uh", ["aggressive","powerful","bold","horns","dramatic"], "Bold K-pop with dramatic brass, powerful rapping, and fierce breakup energy."),
    ("Lovesick Girls", "BLACKPINK", 2020, ["K-pop","pop","rock"], "We are the lovesick girls", ["upbeat","catchy","empowering","guitar","bittersweet"], "Bittersweet pop-rock celebrating stubborn hopefulness in love."),
    ("Gangnam Style", "PSY", 2012, ["K-pop","pop","EDM"], "오빤 강남 스타일", ["fun","viral","dance","absurdist","upbeat"], "Global viral dance phenomenon with absurdist humor and an infectious electronic groove."),
    ("Gee", "Girls' Generation (SNSD)", 2009, ["K-pop","pop"], "", ["bubbly","catchy","bright","sweet","innocent"], "Bubbly, endlessly catchy K-pop debut that defined the innocent girl-group aesthetic."),
    ("Fake Love", "BTS", 2018, ["K-pop","pop","dark pop"], "For you I could pretend like I was happy when I was sad", ["dark","emotional","intense","alt-pop","dramatic"], "Dark, emotionally intense K-pop exploring the pain of losing oneself in a relationship."),
    ("Psycho", "Red Velvet", 2019, ["K-pop","pop","R&B"], "", ["smooth","mysterious","R&B","sophisticated","catchy"], "Smooth, sophisticated K-pop R&B with an irresistible groove and mysterious edge."),
    ("Celebrity", "IU", 2021, ["K-pop","pop"], "", ["upbeat","self-love","bright","sweet","catchy"], "Bright, self-affirming pop celebrating the inner celebrity in everyone."),
    ("MAMA", "EXO", 2012, ["K-pop","pop","EDM"], "", ["dramatic","epic","tribal","EDM","grand"], "Grand, dramatic K-pop epic with tribal chanting and sweeping EDM production."),
    ("LALISA", "Lisa", 2021, ["K-pop","hip-hop","trap"], "", ["fierce","confident","hip-hop","trap","energetic"], "Fierce solo debut showcasing Lisa's dominant rap and high-energy trap production."),
    ("Next Level", "aespa", 2021, ["K-pop","pop","hip-hop"], "", ["surreal","bass-heavy","genre-switching","unique","futuristic"], "Genre-defying K-pop that shifts between multiple distinct sections with futuristic concept."),
    # ── METAL ─────────────────────────────────────────────────────────────────
    ("Master of Puppets", "Metallica", 1986, ["metal","thrash metal"], "Master of puppets, I'm pulling your strings", ["aggressive","complex","anti-drug","driving","iconic"], "Thrash metal landmark about drug addiction—8 minutes of controlled aggression."),
    ("Fade to Black", "Metallica", 1984, ["metal","hard rock","ballad"], "Life, it seems, will fade away", ["dark","melancholic","progressive","heavy","ballad"], "Dark, progressive metal ballad moving from delicate acoustic to crushing heaviness."),
    ("Iron Man", "Black Sabbath", 1970, ["metal","hard rock"], "I am Iron Man", ["dark","heavy","riff-based","proto-metal","iconic"], "Iconic proto-metal riff and a dark science-fiction narrative voiced by a distorted guitar."),
    ("War Pigs", "Black Sabbath", 1970, ["metal","hard rock"], "Generals gathered in their masses", ["dark","anti-war","heavy","epic","progressive"], "Heavy, slow-burning anti-war metal epic with a dramatic structure."),
    ("Raining Blood", "Slayer", 1986, ["metal","thrash metal"], "Trapped in purgatory", ["aggressive","dark","fast","chaotic","extreme"], "Relentless thrash metal assault—one of the genre's definitive extreme tracks."),
    ("Symphony of Destruction", "Megadeth", 1992, ["metal","thrash metal"], "You take a mortal man, and put him in control", ["political","heavy","riff-based","driving","classic"], "Politically charged thrash metal with a crushing main riff and anti-authoritarian message."),
    ("Chop Suey!", "System of a Down", 2001, ["metal","alternative metal"], "Wake up, grab a brush and put a little make-up", ["chaotic","aggressive","political","quirky","intense"], "Chaotic, politically charged metal that lurches between whispered verses and screaming choruses."),
    ("B.Y.O.B.", "System of a Down", 2005, ["metal","alternative metal"], "Why do they always send the poor", ["frenetic","political","anti-war","chaotic","energetic"], "Furious, frenetic anti-war metal with rapid tempo changes and searing political lyrics."),
    ("In the End", "Linkin Park", 2000, ["rock","alternative metal","nu-metal"], "It starts with one thing, I don't know why", ["emotional","rap-rock","anthemic","nu-metal","catchy"], "Emotional rap-rock anthem blending Mike Shinoda's rapping and Chester Bennington's raw vocal."),
    ("Numb", "Linkin Park", 2003, ["rock","alternative metal","nu-metal"], "I'm tired of being what you want me to be", ["emotional","piano","nu-metal","angsty","powerful"], "Piano-driven nu-metal anthem of teenage alienation and the pressure to conform."),
    ("Breaking the Habit", "Linkin Park", 2003, ["rock","alternative metal"], "Memories consume, like opening the wounds", ["emotional","introspective","orchestral","nu-metal","vulnerable"], "Introspective, orchestrally-tinged Linkin Park track about breaking cycles of self-destruction."),
    ("The Beautiful People", "Marilyn Manson", 1996, ["industrial metal","alternative metal"], "Hey you, what do you see?", ["industrial","dark","provocative","aggressive","riff"], "Abrasive industrial metal anthem critiquing beauty standards and social conformity."),
]

EXISTING_MODERN_IDS = [
    (11, "Billie Jean", "Michael Jackson"),
    (12, "Bohemian Rhapsody", "Queen"),
    (13, "Smells Like Teen Spirit", "Nirvana"),
    (14, "Rolling in the Deep", "Adele"),
    (15, "HUMBLE.", "Kendrick Lamar"),
    (16, "Take Five", "The Dave Brubeck Quartet"),
    (17, "Midnight City", "M83"),
    (18, "Get Lucky", "Daft Punk"),
    (19, "Shape of You", "Ed Sheeran"),
    (20, "So What", "Miles Davis"),
]


def fetch_itunes_preview(title, artist):
    term = urllib.parse.quote(f"{artist} {title}")
    url = f"https://itunes.apple.com/search?term={term}&entity=song&limit=5&country=us"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())
        results = data.get("results", [])
        # Prefer a result whose title closely matches
        for track in results:
            if track.get("previewUrl") and title.lower() in track.get("trackName", "").lower():
                return track["previewUrl"]
        # Fallback: first result with any preview
        for track in results:
            if track.get("previewUrl"):
                return track["previewUrl"]
    except Exception as e:
        print(f"  iTunes error: {e}")
    return None


def main():
    conn = sqlite3.connect(DB_PATH)

    # 1. Back-fill iTunes previews for existing modern songs (11-20)
    print("=== Back-filling modern song previews ===")
    for song_id, title, artist in EXISTING_MODERN_IDS:
        print(f"[{song_id}] {title} – {artist} ...", end=" ", flush=True)
        url = fetch_itunes_preview(title, artist)
        print("✓" if url else "✗")
        if url:
            conn.execute("UPDATE songs SET preview_url = ? WHERE id = ?", (url, song_id))
            conn.commit()
        time.sleep(0.2)

    # 2. Add new songs
    print(f"\n=== Adding {len(NEW_SONGS)} new songs ===")
    cur = conn.cursor()
    cur.execute("SELECT MAX(id) FROM songs")
    next_id = (cur.fetchone()[0] or 20) + 1

    for i, (title, artist, year, genres, lyric, moods, desc) in enumerate(NEW_SONGS):
        song_id = next_id + i
        print(f"[{song_id}] {title} – {artist} ...", end=" ", flush=True)
        url = fetch_itunes_preview(title, artist)
        print("✓" if url else "✗")
        conn.execute(
            """INSERT OR IGNORE INTO songs
               (id, title, artist, year, genre, lyric_snippet, mood_keywords, description, preview_url, melody_contour)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (song_id, title, artist, year,
             json.dumps(genres), lyric,
             json.dumps(moods), desc,
             url, json.dumps([])),
        )
        conn.commit()
        time.sleep(0.2)

    conn.close()
    cur2 = sqlite3.connect(DB_PATH).execute("SELECT COUNT(*) FROM songs")
    print(f"\nDone! Total songs in database: {cur2.fetchone()[0]}")


if __name__ == "__main__":
    main()
