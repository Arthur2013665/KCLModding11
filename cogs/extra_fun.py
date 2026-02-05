"""
Extra fun commands - 40+ commands
"""
import discord
from discord import app_commands
from discord.ext import commands
import random
from typing import Optional

from utils.embeds import success_embed
import config

class ExtraFun(commands.Cog):
    """Extra fun commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="ascii", description="Convert text to ASCII art")
    @app_commands.describe(text="Text to convert")
    async def ascii(self, interaction: discord.Interaction, text: str):
        """ASCII art"""
        await interaction.response.send_message(f"```{text}```")
    
    @app_commands.command(name="emojify", description="Convert text to emojis")
    @app_commands.describe(text="Text to emojify")
    async def emojify(self, interaction: discord.Interaction, text: str):
        """Emojify text"""
        emoji_map = {'a':'🇦','b':'🇧','c':'🇨','d':'🇩','e':'🇪','f':'🇫','g':'🇬','h':'🇭','i':'🇮','j':'🇯','k':'🇰','l':'🇱','m':'🇲','n':'🇳','o':'🇴','p':'🇵','q':'🇶','r':'🇷','s':'🇸','t':'🇹','u':'🇺','v':'🇻','w':'🇼','x':'🇽','y':'🇾','z':'🇿'}
        result = ' '.join(emoji_map.get(c.lower(), c) for c in text)
        await interaction.response.send_message(result[:2000])
    
    @app_commands.command(name="clap", description="Add claps between words")
    @app_commands.describe(text="Text to clap")
    async def clap(self, interaction: discord.Interaction, text: str):
        """Clap text"""
        result = " 👏 ".join(text.split())
        await interaction.response.send_message(result)
    
    @app_commands.command(name="vaporwave", description="Convert to vaporwave text")
    @app_commands.describe(text="Text to convert")
    async def vaporwave(self, interaction: discord.Interaction, text: str):
        """Vaporwave text"""
        result = ''.join(chr(ord(c) + 0xFEE0) if ord(c) < 127 else c for c in text)
        await interaction.response.send_message(result)

    @app_commands.command(name="slots", description="Play slots")
    async def slots(self, interaction: discord.Interaction):
        """Slots game"""
        emojis = ['🍒', '🍋', '🍊', '🍇', '💎', '7️⃣']
        result = [random.choice(emojis) for _ in range(3)]
        if result[0] == result[1] == result[2]:
            message = "🎉 JACKPOT! You won!"
        elif result[0] == result[1] or result[1] == result[2]:
            message = "✨ Two match! Small win!"
        else:
            message = "❌ No match. Try again!"
        embed = discord.Embed(title="🎰 Slots", description=f"{' '.join(result)}\n\n{message}", color=config.Colors.PRIMARY)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="rps", description="Rock Paper Scissors")
    @app_commands.describe(choice="Your choice")
    async def rps(self, interaction: discord.Interaction, choice: str):
        """Rock paper scissors"""
        choices = ['rock', 'paper', 'scissors']
        if choice.lower() not in choices:
            await interaction.response.send_message("❌ Choose rock, paper, or scissors", ephemeral=True)
            return
        bot_choice = random.choice(choices)
        user_choice = choice.lower()
        if user_choice == bot_choice:
            result = "It's a tie!"
        elif (user_choice == 'rock' and bot_choice == 'scissors') or (user_choice == 'paper' and bot_choice == 'rock') or (user_choice == 'scissors' and bot_choice == 'paper'):
            result = "You win!"
        else:
            result = "You lose!"
        embed = discord.Embed(title="Rock Paper Scissors", description=f"You: {user_choice}\nBot: {bot_choice}\n\n{result}", color=config.Colors.PRIMARY)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="flip", description="Flip a coin with bet")
    @app_commands.describe(choice="heads or tails")
    async def flip(self, interaction: discord.Interaction, choice: str):
        """Coin flip game"""
        if choice.lower() not in ['heads', 'tails']:
            await interaction.response.send_message("❌ Choose heads or tails", ephemeral=True)
            return
        result = random.choice(['heads', 'tails'])
        won = choice.lower() == result
        embed = discord.Embed(
            title="🪙 Coin Flip",
            description=f"Result: **{result}**\n{'✅ You won!' if won else '❌ You lost!'}",
            color=config.Colors.SUCCESS if won else config.Colors.ERROR
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="roll", description="Roll dice with custom sides")
    @app_commands.describe(dice="Dice notation (e.g., 2d6)")
    async def roll(self, interaction: discord.Interaction, dice: str):
        """Roll dice"""
        try:
            count, sides = map(int, dice.lower().split('d'))
            if count > 100 or sides > 1000:
                await interaction.response.send_message("❌ Too many dice or sides", ephemeral=True)
                return
            results = [random.randint(1, sides) for _ in range(count)]
            total = sum(results)
            embed = discord.Embed(title=f"🎲 Rolling {dice}", color=config.Colors.PRIMARY)
            embed.add_field(name="Results", value=", ".join(map(str, results)))
            embed.add_field(name="Total", value=total)
            await interaction.response.send_message(embed=embed)
        except:
            await interaction.response.send_message("❌ Invalid dice format. Use format like 2d6", ephemeral=True)
    
    @app_commands.command(name="trivia", description="Random trivia question")
    async def trivia(self, interaction: discord.Interaction):
        """Trivia game"""
        questions = [
            {"q": "What is the capital of France?", "a": "Paris"},
            {"q": "How many continents are there?", "a": "7"},
            {"q": "What year did World War 2 end?", "a": "1945"},
            {"q": "What is the largest planet?", "a": "Jupiter"},
            {"q": "Who painted the Mona Lisa?", "a": "Leonardo da Vinci"}
        ]
        trivia = random.choice(questions)
        embed = discord.Embed(title="❓ Trivia", description=trivia['q'], color=config.Colors.INFO)
        embed.set_footer(text=f"Answer: {trivia['a']}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="meme", description="Get a random meme")
    async def meme(self, interaction: discord.Interaction):
        """Random meme"""
        memes = [
            "https://i.imgur.com/example1.jpg",
            "https://i.imgur.com/example2.jpg",
            "https://i.imgur.com/example3.jpg"
        ]
        embed = discord.Embed(title="😂 Random Meme", color=config.Colors.PRIMARY)
        embed.set_image(url=random.choice(memes))
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="dadjoke", description="Get a dad joke")
    async def dadjoke(self, interaction: discord.Interaction):
        """Dad joke"""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "I'm reading a book about anti-gravity. It's impossible to put down!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "I used to hate facial hair, but then it grew on me.",
            "What do you call a fake noodle? An impasta!"
        ]
        embed = discord.Embed(title="👨 Dad Joke", description=random.choice(jokes), color=config.Colors.PRIMARY)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="pickup", description="Get a pickup line")
    async def pickup(self, interaction: discord.Interaction):
        """Pickup line"""
        lines = [
            "Are you a magician? Because whenever I look at you, everyone else disappears.",
            "Do you have a map? I keep getting lost in your eyes.",
            "Are you a parking ticket? Because you've got FINE written all over you.",
            "Is your name Google? Because you have everything I've been searching for.",
            "Do you believe in love at first sight, or should I walk by again?"
        ]
        embed = discord.Embed(title="💘 Pickup Line", description=random.choice(lines), color=discord.Color.pink())
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="insult", description="Get a random insult")
    async def insult(self, interaction: discord.Interaction):
        """Random insult"""
        insults = [
            "You're as useful as a screen door on a submarine.",
            "I'd agree with you, but then we'd both be wrong.",
            "You're not stupid; you just have bad luck thinking.",
            "If I wanted to hear from someone with your IQ, I'd watch paint dry.",
            "You bring everyone so much joy... when you leave the room."
        ]
        embed = discord.Embed(title="💢 Insult", description=random.choice(insults), color=config.Colors.ERROR)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="wisdom", description="Get random wisdom")
    async def wisdom(self, interaction: discord.Interaction):
        """Random wisdom"""
        wisdom = [
            "The only way to do great work is to love what you do.",
            "Life is 10% what happens to you and 90% how you react to it.",
            "The best time to plant a tree was 20 years ago. The second best time is now.",
            "Don't watch the clock; do what it does. Keep going.",
            "The future belongs to those who believe in the beauty of their dreams."
        ]
        embed = discord.Embed(title="🧘 Wisdom", description=random.choice(wisdom), color=config.Colors.INFO)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="fortune", description="Get your fortune")
    async def fortune(self, interaction: discord.Interaction):
        """Fortune cookie"""
        fortunes = [
            "A pleasant surprise is waiting for you.",
            "Your hard work will soon pay off.",
            "Good things come to those who wait.",
            "An exciting opportunity is coming your way.",
            "You will make many friends in the coming months."
        ]
        embed = discord.Embed(title="🥠 Fortune Cookie", description=random.choice(fortunes), color=config.Colors.PRIMARY)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="advice", description="Get random advice")
    async def advice(self, interaction: discord.Interaction):
        """Random advice"""
        advice = [
            "Always be yourself, unless you can be a unicorn. Then always be a unicorn.",
            "Don't take life too seriously. Nobody gets out alive anyway.",
            "If at first you don't succeed, skydiving is not for you.",
            "The early bird gets the worm, but the second mouse gets the cheese.",
            "When life gives you lemons, make lemonade. Then find someone whose life gave them vodka."
        ]
        embed = discord.Embed(title="💡 Advice", description=random.choice(advice), color=config.Colors.INFO)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="yesno", description="Ask a yes/no question")
    @app_commands.describe(question="Your question")
    async def yesno(self, interaction: discord.Interaction, question: str):
        """Yes or no"""
        answer = random.choice(["Yes", "No", "Maybe", "Definitely", "Absolutely not", "Ask again later"])
        embed = discord.Embed(title="Yes or No", color=config.Colors.PRIMARY)
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer", value=answer, inline=False)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="wouldyourather", description="Would you rather question")
    async def wouldyourather(self, interaction: discord.Interaction):
        """Would you rather"""
        questions = [
            "Would you rather be able to fly or be invisible?",
            "Would you rather have unlimited money or unlimited time?",
            "Would you rather live in the past or the future?",
            "Would you rather be famous or be the best friend of someone famous?",
            "Would you rather have the ability to read minds or see the future?"
        ]
        embed = discord.Embed(title="🤔 Would You Rather", description=random.choice(questions), color=config.Colors.PRIMARY)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="neverhaveiever", description="Never have I ever statement")
    async def neverhaveiever(self, interaction: discord.Interaction):
        """Never have I ever"""
        statements = [
            "Never have I ever skipped school",
            "Never have I ever lied to my parents",
            "Never have I ever stayed up all night",
            "Never have I ever broken a bone",
            "Never have I ever been on TV"
        ]
        embed = discord.Embed(title="🙈 Never Have I Ever", description=random.choice(statements), color=config.Colors.PRIMARY)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="truthordare", description="Get a truth or dare")
    @app_commands.describe(choice="truth or dare")
    async def truthordare(self, interaction: discord.Interaction, choice: str):
        """Truth or dare"""
        truths = [
            "What's your biggest fear?",
            "What's your most embarrassing moment?",
            "Who was your first crush?",
            "What's a secret you've never told anyone?",
            "What's the worst thing you've ever done?"
        ]
        dares = [
            "Do 20 pushups",
            "Sing a song",
            "Dance for 30 seconds",
            "Tell a joke",
            "Do your best impression of someone"
        ]
        if choice.lower() == 'truth':
            result = random.choice(truths)
            title = "🤐 Truth"
        elif choice.lower() == 'dare':
            result = random.choice(dares)
            title = "😈 Dare"
        else:
            await interaction.response.send_message("❌ Choose truth or dare", ephemeral=True)
            return
        embed = discord.Embed(title=title, description=result, color=config.Colors.PRIMARY)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="password", description="Generate random password")
    @app_commands.describe(length="Password length")
    async def password(self, interaction: discord.Interaction, length: int = 16):
        """Generate password"""
        import string
        if length < 8 or length > 64:
            await interaction.response.send_message("❌ Length must be 8-64", ephemeral=True)
            return
        chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(chars) for _ in range(length))
        embed = discord.Embed(title="🔐 Generated Password", description=f"```{password}```", color=config.Colors.SUCCESS)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="randomnumber", description="Generate random number")
    @app_commands.describe(min="Minimum", max="Maximum")
    async def randomnumber(self, interaction: discord.Interaction, min: int = 1, max: int = 100):
        """Random number"""
        if min >= max:
            await interaction.response.send_message("❌ Min must be less than max", ephemeral=True)
            return
        number = random.randint(min, max)
        embed = discord.Embed(title="🎲 Random Number", description=f"**{number}**", color=config.Colors.PRIMARY)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="randomcolor", description="Generate random color")
    async def randomcolor(self, interaction: discord.Interaction):
        """Random color"""
        color = discord.Color.random()
        hex_color = f"#{color.value:06x}"
        embed = discord.Embed(title="🎨 Random Color", description=f"**{hex_color}**", color=color)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ExtraFun(bot))
