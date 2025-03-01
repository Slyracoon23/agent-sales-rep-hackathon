// Define the type for conversation steps
export type ConversationStep = {
  agent: "sales_agent" | "customer_agent";
  message: string;
};

// The complete sales conversation
export const fullConversation: ConversationStep[] = [
  {
    agent: "customer_agent",
    message: "Hello? It's Mike."
  },
  {
    agent: "sales_agent",
    message: "Hi, Mike. My name is Max. I was hoping I could speak with whoever's in charge for you guys' billing and invoicing, please."
  },
  {
    agent: "customer_agent",
    message: "Doing a what?"
  },
  {
    agent: "sales_agent",
    message: "Billing and invoicing, please."
  },
  {
    agent: "customer_agent",
    message: "You're speaking to him."
  },
  {
    agent: "sales_agent",
    message: "Oh, fantastic. I was calling because I've been working with a few other contractors around the area and got sent overseas guys and your website. And it looks great, but I noticed you guys don't seem to have a way for your clients"
  },
  {
    agent: "customer_agent",
    message: "Hey. You know what?"
  },
  {
    agent: "sales_agent",
    message: "to do that. Oh, yeah?"
  },
  {
    agent: "customer_agent",
    message: "I am so excited you say great because everybody called that tried to sell me on something, says it's horrible, and you can't find it. And my joke is, how is that possible? You found me because you called me. Anyways, go ahead. I I hear your spiel, and I'll tell you what's up. But go ahead."
  },
  {
    agent: "sales_agent",
    message: "Oh, for sure. Yeah. I was"
  },
  {
    agent: "customer_agent",
    message: "I'm listening."
  },
  {
    agent: "sales_agent",
    message: "just I was just gonna mention, look at an a portal for clients to view their invoices online or anything like that."
  },
  {
    agent: "customer_agent",
    message: "Hi. Here's the deal. This is how my business works. I do everything through QuickBooks. Okay? I'm gonna make it pretty quick for you. Everything I have is on QuickBooks. How people pay me, ninety five percent of the people that I do work for. It's a double check deal. It's usually the bank oh, I'm sorry. The builder and the and the there's there's two parties because they're big projects. So it's the the the two the contractor and it's the development company. So they double sign. I get a"
  },
  {
    agent: "sales_agent",
    message: "Yeah."
  },
  {
    agent: "customer_agent",
    message: "check. That's how and it comes in the mail. That is honestly seventy five percent of my business. Anything else service wise, nine out of ten times is Zeller"
  },
  {
    agent: "sales_agent",
    message: "Okay."
  },
  {
    agent: "customer_agent",
    message: "by Mo. And then your basic people, like, some of my smaller built, it's checks. And that's it. I hardly"
  },
  {
    agent: "sales_agent",
    message: "I got you."
  },
  {
    agent: "customer_agent",
    message: "ever get I mean, once in a while, I get people going, hey. You know what? I I ok'd the project. I was gonna pay it through QuickBooks. I go, I didn't have them set up. They're all okay. We'll just leave you a check or Venmo. And and it's just not like that. We"
  },
  {
    agent: "sales_agent",
    message: "Okay."
  },
  {
    agent: "customer_agent",
    message: "don't do we don't do a ton of service work. Unfortunately, I'm doing service right now."
  },
  {
    agent: "sales_agent",
    message: "I got you."
  },
  {
    agent: "customer_agent",
    message: "But yeah. It's not like that. I mean,"
  },
  {
    agent: "sales_agent",
    message: "I hear you."
  },
  {
    agent: "customer_agent",
    message: "my business and it's the same people I knew forever almost, it seems like."
  },
  {
    agent: "sales_agent",
    message: "Absolutely. Yeah."
  },
  {
    agent: "customer_agent",
    message: "Yeah. Yeah."
  },
  {
    agent: "sales_agent",
    message: "So I guess I'll explain a little bit about what we are. So we're a company called Trust Payments. We work with contractors around the US. We help you guys get paid faster and try and help you save thousands on processing fees. So for example, you can think of it a little bit like a bank account for contractors. We don't actually replace QuickBooks. We have a two way integration with them, so we should sync seamlessly."
  },
  {
    agent: "customer_agent",
    message: "Mhmm."
  },
  {
    agent: "sales_agent",
    message: "But the way it would look is"
  },
  {
    agent: "customer_agent",
    message: "So I know. Somebody called me. Yeah. You guys would be"
  },
  {
    agent: "sales_agent",
    message: "oh, you're all good."
  },
  {
    agent: "customer_agent",
    message: "the bank. You would guarantee the checks. If the check would go bad, as soon as it comes up, the check goes to you. It's good. It's a certain percent, one percent, or certain percent. I I think I know what it is already because I'm the only guy."
  },
  {
    agent: "sales_agent",
    message: "Oh, wait. We don't actually charge any fees. It's it's similar to what"
  },
  {
    agent: "customer_agent",
    message: "Okay."
  },
  {
    agent: "sales_agent",
    message: "you're describing, but not exactly. We don't have any fees, and the whole idea is with us, you'll be able to accept any form of payment. It'll never cost you anything, and we have instant settlement. So whether it's credit card, check, ACH, you got mobile deposit, all that kind of stuff, that'll deposit into your account instantly, and you'll never be charged any fees for accepting any form of payment. And we have no, like, monthly"
  },
  {
    agent: "customer_agent",
    message: "Okay."
  },
  {
    agent: "sales_agent",
    message: "or annual fees as well, so we're a free to use service for"
  },
  {
    agent: "customer_agent",
    message: "What's the catch? There's gotta be a catch. You're not calling me just because you're my charming personality and you're gonna do stuff for free. I mean, here's the deal."
  },
  {
    agent: "sales_agent",
    message: "No. Absolutely not. I mean"
  },
  {
    agent: "customer_agent",
    message: "I I I"
  },
  {
    agent: "sales_agent",
    message: "yeah."
  },
  {
    agent: "customer_agent",
    message: "I my business, the only people I'm late on payments on, and I know it's because it's sixty five days, and usually they're about seventy, seventy five. But I'm not gonna argue with them because they spend about, I don't know, two million a year with me. So I can't fight them over"
  },
  {
    agent: "sales_agent",
    message: "Fair enough."
  },
  {
    agent: "customer_agent",
    message: "ten days. Right?"
  },
  {
    agent: "sales_agent",
    message: "For"
  },
  {
    agent: "customer_agent",
    message: "You know, the guy I wanna"
  },
  {
    agent: "sales_agent",
    message: "sure."
  },
  {
    agent: "customer_agent",
    message: "kill is the guy who owes me, like, sixty five dollars. And and I'm like, really? And there's about two of those a year. And it's not even worth arguing"
  },
  {
    agent: "sales_agent",
    message: "Yeah. For sure."
  },
  {
    agent: "customer_agent",
    message: "with those guys. What the"
  },
  {
    agent: "sales_agent",
    message: "No. Never."
  },
  {
    agent: "customer_agent",
    message: "hell? Why is my thing not sending a signal now? I'm sorry. I'm trying to diagnose something while we're talking."
  },
  {
    agent: "sales_agent",
    message: "No. You're all good. I understand."
  },
  {
    agent: "customer_agent",
    message: "Yeah. Anyways, I don't know if that's I mean, you know, I'm not trying to talk. I'm it's just we've been here twenty six years. What I got works. We're small. I got five guys. I got my daughter works part time. My business partner and I, so that's seven people. So we have seven and a half people. It just it works. It's just simple. Everybody like I said, I it's my my biggest confusing thing of the honestly, of all this is is is when people send me checks that have nothing to do with their name. You know what I'm saying? That's the hardest thing"
  },
  {
    agent: "sales_agent",
    message: "Yeah."
  },
  {
    agent: "customer_agent",
    message: "I no. Like like your name is John Smith. Okay? Well, your wife doesn't go by Susie Smith. She goes by Susie Atkins. Still. You"
  },
  {
    agent: "sales_agent",
    message: "Oh, no."
  },
  {
    agent: "customer_agent",
    message: "know what I mean? And then she"
  },
  {
    agent: "sales_agent",
    message: "Yeah."
  },
  {
    agent: "customer_agent",
    message: "sends me a check from Susie Atkins. I have no idea who the hell Susie Atkins is, and I'm like, and they don't put an invoice number. I'm like, what is this three hundred and eighty dollar check for? Then I go through all this stuff and I go, I only have one invoice for three eighty. Then I call them and I go, hey, John, is there any chance your wife's name is Susie Atkins? Yeah. It is."
  },
  {
    agent: "sales_agent",
    message: "Yeah."
  },
  {
    agent: "customer_agent",
    message: "Okay. Thanks. Because I had no idea where this check came from. And then it comes from a PO box. You know what I mean? That is truthfully my biggest hurdle I have besides needing more employees."
  },
  {
    agent: "sales_agent",
    message: "So"
  },
  {
    agent: "customer_agent",
    message: "But that's it, really, man. I"
  },
  {
    agent: "sales_agent",
    message: "I actually think we could take care of that for you, man. So the way it works is with that mobile check deposit, right, as well as the integration with QuickBooks,"
  },
  {
    agent: "customer_agent",
    message: "uh-huh."
  },
  {
    agent: "sales_agent",
    message: "it will see that. It will match it to the exact amount. It'll say, oh, this is clearly that. Right? It should do it automatically for you so you don't have to worry about any"
  },
  {
    agent: "customer_agent",
    message: "But what do you what do you do when which I do have, this is true, I do have, I have a shitload of two hundred and sixty five dollar ones. Because just a basic little in and out two hundred sixty five bucks. So that's all by, like, Zelle and Venmo. So how would they recognize"
  },
  {
    agent: "sales_agent",
    message: "For sure."
  },
  {
    agent: "customer_agent",
    message: "that unless you pulled up their name? And that's easy. I just looked at my stuff. Zelle is Venmo is easy. I just look and go, okay. I could see who it is or And I always tell the people from Infernal, please put your address with it. You know you know, that's easy, but when they send it to me anyways."
  },
  {
    agent: "sales_agent",
    message: "So it should link automatically through QuickBooks based on the invoice number. If it isn't the invoice number if it doesn't have an invoice number or anything relating to"
  },
  {
    agent: "customer_agent",
    message: "No. That's the problem. Don't send me a check thinking"
  },
  {
    agent: "sales_agent",
    message: "the customer, like, you're giving me a response number."
  },
  {
    agent: "customer_agent",
    message: "I'm their only client. The only person I've ever done work for was just this one person. They send me a check, and then, you know, they don't put any information down."
  },
  {
    agent: "sales_agent",
    message: "Yeah. Yeah. So even if there's no information, if there's one, like, check and one invoice that are matching amounts, it should match them automatically. If it's got multiple, then it will try and use an invoice number. So, like, if you have multiple for the exact same amount that don't have an invoice number,"
  },
  {
    agent: "customer_agent",
    message: "Uh-huh."
  },
  {
    agent: "sales_agent",
    message: "that you'll probably have to do manually."
  },
  {
    agent: "customer_agent",
    message: "So so what is what's my benefit? I don't understand."
  },
  {
    agent: "sales_agent",
    message: "yeah?"
  },
  {
    agent: "customer_agent",
    message: "What's what's my benefit on this?"
  },
  {
    agent: "sales_agent",
    message: "The benefit should hopefully be"
  },
  {
    agent: "customer_agent",
    message: "Just entering just entering entering checks? What is my benefit?"
  },
  {
    agent: "sales_agent",
    message: "it should be easier for you to enter checks. You guys shouldn't have to do that. We can authorize employees to do mobile deposits so you don't have to worry about employees bringing checks back to you so you can deposit them yourself. Shouldn't have to do any"
  },
  {
    agent: "customer_agent",
    message: "So"
  },
  {
    agent: "sales_agent",
    message: "more bank run. You should be able to accept"
  },
  {
    agent: "customer_agent",
    message: "I I like I like doing actually, I'm one of the weird ones. I like doing banking just because"
  },
  {
    agent: "sales_agent",
    message: "pretty much anything."
  },
  {
    agent: "customer_agent",
    message: "yeah. You know what? No. Seriously. You know why I like it? It's because my bank knows me. Otherwise, they don't know who the hell I am. And I have several several accounts of money in my bank between my personal, my business, my house couple houses I own that I you know what I mean? So anytime I want"
  },
  {
    agent: "sales_agent",
    message: "For sure."
  },
  {
    agent: "customer_agent",
    message: "something, it's they treat me really well. Just because"
  },
  {
    agent: "sales_agent",
    message: "For sure."
  },
  {
    agent: "customer_agent",
    message: "you know what I mean? I'm it's you're I can tell you're pretty young, but, man, I'll tell you something just talking to you, and I'm sure you're very educated. But what I'm what I'm getting at is there's nothing like actually seeing a person. Like, my my jobs I do, first thing I ask them when you someone calls me up, I go, hey. Never heard these people before. Never. I go, how'd you get a hold of me? When you tell me it's they got us through faith like like, if you were on through a person that, you know, somebody I know. I know right away. It's a job. It's gonna be legit. I don't have to go there and waste my time. You know what I mean? I I'm already"
  },
  {
    agent: "sales_agent",
    message: "Absolutely. Yeah."
  },
  {
    agent: "customer_agent",
    message: "in the door. All I gotta do is show up. If it's if it's Nextdoor, I got great reviews on Nextdoor. And there's certain subdivisions. They go, yeah. We got you off Nextdoor, and they always say you got great reviews. I'll take care of it right away. I'll jump right on it. And and those people those people pay right away always. But otherwise, I just don't know what really that my benefit is besides entering my check. And the one nice thing about that is is not that I can run or can't run a report to QuickBooks and see that, what people who paid and who didn't. It's just kinda nice to look at it and go, okay. This much is I mean, I can run a it gives me a reason to look at who owes me money and who doesn't. You know. And the main thing is it's builders. It's not homeowners because nine out of ten times, I'd tell them that they pay immediately or really within a week or so. It's the builders I can notice. Oh, okay. This one's, like, you know, seventy two days out. We gotta we gotta give them a call. You know? And and like I say, we"
  },
  {
    agent: "sales_agent",
    message: "Yeah. Absolutely."
  },
  {
    agent: "customer_agent",
    message: "have sixty five days on most of the stuff. But it's but"
  },
  {
    agent: "sales_agent",
    message: "Yeah. So with us, with those invoices, you should be able to see all of them just the same way, but we can actually send out those reminders, through trust, through that account. We can send them out for you. And then, similarly,"
  },
  {
    agent: "customer_agent",
    message: "or I can do it through QuickBooks too. That's because they have a"
  },
  {
    agent: "sales_agent",
    message: "we could also"
  },
  {
    agent: "customer_agent",
    message: "reminder right through QuickBooks. Because I have my my QuickBooks set up where, you know well, I don't have it on my big builders, but I have it set up after"
  },
  {
    agent: "sales_agent",
    message: "you could do it through QuickBooks."
  },
  {
    agent: "customer_agent",
    message: "forty days, they get a reminder. The big the the"
  },
  {
    agent: "sales_agent",
    message: "Yeah."
  },
  {
    agent: "customer_agent",
    message: "the yeah. So I don't know again, I just don't know where it's gonna benefit me. I mean, it really we're not that techie. It's pretty simple, man. We just we just do our stuff through QuickBooks, and I do my estimates through there, and I'm just easy. It's just I've been doing it for"
  },
  {
    agent: "sales_agent",
    message: "For sure."
  },
  {
    agent: "customer_agent",
    message: "twenty six. I know it's a I know it sound like a dinosaur because I am, but I've been doing this for twenty six years, and it just works."
  },
  {
    agent: "sales_agent",
    message: "No. I hate you, man. Don't fix what's not broken. Right?"
  },
  {
    agent: "customer_agent",
    message: "You know? No. I mean, the shit works, and I make money, and I I'm in good shape. So my I have some of the same employees"
  },
  {
    agent: "sales_agent",
    message: "Absolutely."
  },
  {
    agent: "customer_agent",
    message: "for twenty years, so I must be being doing something"
  },
  {
    agent: "sales_agent",
    message: "I like it."
  },
  {
    agent: "customer_agent",
    message: "half decent."
  },
  {
    agent: "sales_agent",
    message: "Exactly. Yeah. So I think"
  },
  {
    agent: "customer_agent",
    message: "So"
  },
  {
    agent: "sales_agent",
    message: "the biggest advantage for you with us would be the ability to take ACH payments instead of check. It would save you a ton of time, and then and most people tend to avoid them because of the hold periods, because of the fees. With us, we try and get rid of them because we know that hurts your business the most, and so we try and help you guys out there. And that would hopefully eliminate most of the time you're spending on checks. But I also understand that's a"
  },
  {
    agent: "customer_agent",
    message: "Like, what"
  },
  {
    agent: "sales_agent",
    message: "transition you guys don't"
  },
  {
    agent: "customer_agent",
    message: "what times am I what time am I spending on checks that day? I I'm not following you. Short of getting it and"
  },
  {
    agent: "sales_agent",
    message: "Just being"
  },
  {
    agent: "customer_agent",
    message: "going to the bank with it. I mean, I can just do it through my phone,"
  },
  {
    agent: "sales_agent",
    message: "yeah."
  },
  {
    agent: "customer_agent",
    message: "and I can deposit them. Like but I I I actually I'm sixty one. I enjoy I actually enjoy going to the bank. Today, I'm going to the bank. My deposit today is gonna be about a hundred and ninety thousand. Okay? So I I enjoy"
  },
  {
    agent: "sales_agent",
    message: "Dang, man. Impressive."
  },
  {
    agent: "customer_agent",
    message: "going there. That that's that's a small one of my checks, and I I won't even go under fifty thousand, I wouldn't walk. I won't even go to the bank. But like I say, I just the thing is is I just don't even I enjoy going. I enjoy seeing those people. They all I just I like it. It's just call me old, man. I like that shit. But I I don't know what the real again, I don't know what my benefit would be. I just don't know where it's gonna make my life any easier besides having one"
  },
  {
    agent: "sales_agent",
    message: "No. That's fair, man."
  },
  {
    agent: "customer_agent",
    message: "more thing to deal with. You know what I mean? Besides I have one more thing"
  },
  {
    agent: "sales_agent",
    message: "No. I understand."
  },
  {
    agent: "customer_agent",
    message: "to have to fucking deal with. And I'm just like"
  },
  {
    agent: "sales_agent",
    message: "Absolutely."
  },
  {
    agent: "customer_agent",
    message: "I mean, I know it can integrate with it. I don't know. And I got and and, like, everything else I do to do with, like, my my, you know, reconciliation, all that, my accountant does that. I have she's on my payroll, so she does all that stuff. I"
  },
  {
    agent: "sales_agent",
    message: "For sure."
  },
  {
    agent: "customer_agent",
    message: "all I do is I, you know, I showed it was paid. She takes care of everything else for me. And, you know,"
  },
  {
    agent: "sales_agent",
    message: "I like it."
  },
  {
    agent: "customer_agent",
    message: "like so I just I just don't see it. I appreciate I know I'm a hard sell, but I don't I don't"
  },
  {
    agent: "sales_agent",
    message: "No. And I appreciate"
  },
  {
    agent: "customer_agent",
    message: "really see where my"
  },
  {
    agent: "sales_agent",
    message: "you speaking with me, man. Giving me some education."
  },
  {
    agent: "customer_agent",
    message: "yeah."
  },
  {
    agent: "sales_agent",
    message: "I like it."
  },
  {
    agent: "customer_agent",
    message: "No. And, again, like, I'm sure there's some way somehow that could benefit me. I just don't know if it's really worth my time, man. I just it just what I got works. I still use an Android. Okay? Because I don't wanna"
  },
  {
    agent: "sales_agent",
    message: "For sure."
  },
  {
    agent: "customer_agent",
    message: "switch to an iPhone. You know what I mean? Main"
  },
  {
    agent: "sales_agent",
    message: "I like it."
  },
  {
    agent: "customer_agent",
    message: "reason is the main reason is because the battery life. That's the truth. The battery"
  },
  {
    agent: "sales_agent",
    message: "That's true. Yeah. That does"
  },
  {
    agent: "customer_agent",
    message: "life is so much better."
  },
  {
    agent: "sales_agent",
    message: "nice."
  },
  {
    agent: "customer_agent",
    message: "Yeah. I don't know where you're"
  },
  {
    agent: "sales_agent",
    message: "Yeah."
  },
  {
    agent: "customer_agent",
    message: "out of. Where are you out of? What's what state? You're not out of Arizona, obviously, with that area"
  },
  {
    agent: "sales_agent",
    message: "No. I'm in I'm in California."
  },
  {
    agent: "customer_agent",
    message: "code. Okay. Well, in the summer when it's about"
  },
  {
    agent: "sales_agent",
    message: "Yeah."
  },
  {
    agent: "customer_agent",
    message: "a hundred and twenty here and you're just roasting, my I my"
  },
  {
    agent: "sales_agent",
    message: "Yeah."
  },
  {
    agent: "customer_agent",
    message: "everybody's running around trying to charge their iPhones and they're overheating. Something to do with my Samsung. It just it just man, everything just keeps going, and it holds charge the whole day. And it's in my pocket, and it's hot as hell out. So I don't bathroom. So I don't you know what I mean? That's one reason why I didn't change that, but"
  },
  {
    agent: "sales_agent",
    message: "No. For sure."
  },
  {
    agent: "customer_agent",
    message: "I'm a hard sell on change, man. I really am. But I I appreciate"
  },
  {
    agent: "sales_agent",
    message: "No worries."
  },
  {
    agent: "customer_agent",
    message: "it. But there is if there is a way you would tell me that I didn't have to go to work and shit would get done, I'd be on board, man. But I had to go prove. When you have employees, you better show up at work because they don't I don't care how good your guys are. They don't get shit done unless you're there. You know? I they do,"
  },
  {
    agent: "sales_agent",
    message: "I'll take that under"
  },
  {
    agent: "customer_agent",
    message: "but"
  },
  {
    agent: "sales_agent",
    message: "but no. Yeah. It's not the"
  },
  {
    agent: "customer_agent",
    message: "they don't. They don't."
  },
  {
    agent: "sales_agent",
    message: "same."
  },
  {
    agent: "customer_agent",
    message: "No one wants to be accountable. My guys are if there's one glitch, they wanna push to the curb for another day. You know? And if I'm there, I it gets done. So and I got good guys. That's a scary thing. I got really good guys. But, anyways, hey."
  },
  {
    agent: "sales_agent",
    message: "I know. You're saying they've been forever."
  },
  {
    agent: "customer_agent",
    message: "I'm trying I'm say that again."
  },
  {
    agent: "sales_agent",
    message: "I said I know. You've been saying they were with you forever for, like, twenty years. Right?"
  },
  {
    agent: "customer_agent",
    message: "Yeah. No. Some of them yeah. Some of them some of them have. I got good guys, and I still wanna kill them. But, you know, I appreciate it, man. It's I know you're trying to make a you know, something happen, and it might work well. But right now, it's just not the right time for me. And it's not even a"
  },
  {
    agent: "sales_agent",
    message: "Yeah. No. Totally understand."
  },
  {
    agent: "customer_agent",
    message: "money issue by itself. It just I just don't need more steps in my life. I got plenty of things going"
  },
  {
    agent: "sales_agent",
    message: "No. I get that."
  },
  {
    agent: "customer_agent",
    message: "on. Okay. Hey. I'm gonna go because"
  },
  {
    agent: "sales_agent",
    message: "You're fine, man. Thank you for speaking"
  },
  {
    agent: "customer_agent",
    message: "I'm trying to diagnose a problem"
  },
  {
    agent: "sales_agent",
    message: "with me."
  },
  {
    agent: "customer_agent",
    message: "here. So"
  },
  {
    agent: "sales_agent",
    message: "Yeah. No. Absolutely. Get back to it. Thank you for"
  },
  {
    agent: "customer_agent",
    message: "okay. Very good. It was"
  },
  {
    agent: "sales_agent",
    message: "your time, man."
  },
  {
    agent: "customer_agent",
    message: "no. You're welcome. Good luck. Thank you."
  },
  {
    agent: "sales_agent",
    message: "Of course. Thank you. Good luck. You too."
  },
  {
    agent: "customer_agent",
    message: "Okay. Thank"
  },
  {
    agent: "sales_agent",
    message: "Have a good one."
  },
  {
    agent: "customer_agent",
    message: "you. Okay. Bye bye."
  },
  {
    agent: "sales_agent",
    message: "Bye."
  }
];

// Define the start point for the conversation (index of where to start in the full conversation)
// Set this to 0 to start from the beginning, or to another index if you want to start from a different point
export const conversationStartPoint = 0;

// Extract the initial conversation based on the start point
export function getInitialConversation(length: number = 5): ConversationStep[] {
  return fullConversation.slice(conversationStartPoint, conversationStartPoint + length);
}

// Get conversation starting from a specific index
export function getConversationFromIndex(startIndex: number, length: number = 5): ConversationStep[] {
  if (startIndex < 0 || startIndex >= fullConversation.length) {
    throw new Error(`Invalid start index: ${startIndex}. Must be between 0 and ${fullConversation.length - 1}`);
  }
  return fullConversation.slice(startIndex, startIndex + length);
} 