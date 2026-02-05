"""
Fun and entertainment commands cog
"""
import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio
from typing import Optional

from utils.constants import EIGHTBALL_RESPONSES, ROASTS, COMPLIMENTS, FACTS, QUOTES, JOKES, HACK_MESSAGES
import config

class Fun(commands.Cog):
    """Fun and entertainment commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="8ball", description="Ask the magic 8-ball a question")
    @app_commands.describe(question="Your question")
    async def eightball(self, interaction: discord.Interaction, question: str):
        """Magic 8-ball"""
        response = random.choice(EIGHTBALL_RESPONSES)
        
        embed = discord.Embed(
            title="🎱 Magic 8-Ball",
            color=config.Colors.PRIMARY
        )
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer", value=response, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="coinflip", description="Flip a coin")
    async def coinflip(self, interaction: discord.Interaction):
        """Flip a coin"""
        result = random.choice(['Heads', 'Tails'])
        
        embed = discord.Embed(
            title="🪙 Coin Flip",
            description=f"The coin landed on: **{result}**",
            color=config.Colors.PRIMARY
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="dice", description="Roll a dice")
    @app_commands.describe(sides="Number of sides (default: 6)")
    async def dice(self, interaction: discord.Interaction, sides: int = 6):
        """Roll a dice"""
        if sides < 2:
            await interaction.response.send_message(
                "❌ Dice must have at least 2 sides!",
                ephemeral=True
            )
            return
        
        if sides > 100:
            await interaction.response.send_message(
                "❌ Dice cannot have more than 100 sides!",
                ephemeral=True
            )
            return
        
        result = random.randint(1, sides)
        
        embed = discord.Embed(
            title="🎲 Dice Roll",
            description=f"You rolled a **{result}** (d{sides})",
            color=config.Colors.PRIMARY
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="joke", description="Get a random joke")
    async def joke(self, interaction: discord.Interaction):
        """Random joke"""
        joke = random.choice(JOKES)
        
        embed = discord.Embed(
            title="😂 Random Joke",
            description=joke,
            color=config.Colors.PRIMARY
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="fact", description="Get a random fact")
    async def fact(self, interaction: discord.Interaction):
        """Random fact"""
        fact = random.choice(FACTS)
        
        embed = discord.Embed(
            title="💡 Random Fact",
            description=fact,
            color=config.Colors.INFO
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="quote", description="Get an inspirational quote")
    async def quote(self, interaction: discord.Interaction):
        """Inspirational quote"""
        quote = random.choice(QUOTES)
        
        embed = discord.Embed(
            title="✨ Inspirational Quote",
            description=quote,
            color=config.Colors.PRIMARY
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="roast", description="Roast someone")
    @app_commands.describe(user="User to roast (optional)")
    async def roast(
        self,
        interaction: discord.Interaction,
        user: Optional[discord.Member] = None
    ):
        """Roast someone"""
        target = user or interaction.user
        roast = random.choice(ROASTS)
        
        embed = discord.Embed(
            title="🔥 Roasted!",
            description=f"{target.mention}, {roast}",
            color=config.Colors.ERROR
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="compliment", description="Compliment someone")
    @app_commands.describe(user="User to compliment (optional)")
    async def compliment(
        self,
        interaction: discord.Interaction,
        user: Optional[discord.Member] = None
    ):
        """Compliment someone"""
        target = user or interaction.user
        compliment = random.choice(COMPLIMENTS)
        
        embed = discord.Embed(
            title="💝 Compliment",
            description=f"{target.mention}, {compliment}",
            color=config.Colors.SUCCESS
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="ship", description="Ship two users")
    @app_commands.describe(
        user1="First user",
        user2="Second user"
    )
    async def ship(
        self,
        interaction: discord.Interaction,
        user1: discord.Member,
        user2: discord.Member
    ):
        """Ship two users"""
        # Generate consistent percentage based on user IDs
        combined = user1.id + user2.id
        percentage = (combined % 101)
        
        # Create ship name
        name1 = user1.display_name[:len(user1.display_name)//2]
        name2 = user2.display_name[len(user2.display_name)//2:]
        ship_name = name1 + name2
        
        # Determine message based on percentage
        if percentage < 25:
            message = "Not meant to be... 💔"
            color = config.Colors.ERROR
        elif percentage < 50:
            message = "There's a chance! 💛"
            color = config.Colors.WARNING
        elif percentage < 75:
            message = "Looking good! 💚"
            color = config.Colors.SUCCESS
        else:
            message = "Perfect match! 💖"
            color = config.Colors.PRIMARY
        
        # Create progress bar
        filled = percentage // 10
        bar = "█" * filled + "░" * (10 - filled)
        
        embed = discord.Embed(
            title=f"💕 {ship_name}",
            description=f"{user1.mention} 💕 {user2.mention}",
            color=color
        )
        embed.add_field(
            name="Compatibility",
            value=f"`{bar}` **{percentage}%**\n{message}",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="choose", description="Choose between options")
    @app_commands.describe(options="Options separated by commas")
    async def choose(self, interaction: discord.Interaction, options: str):
        """Choose between options"""
        choices = [opt.strip() for opt in options.split(',')]
        
        if len(choices) < 2:
            await interaction.response.send_message(
                "❌ Please provide at least 2 options separated by commas!",
                ephemeral=True
            )
            return
        
        choice = random.choice(choices)
        
        embed = discord.Embed(
            title="🤔 I Choose...",
            description=f"**{choice}**",
            color=config.Colors.PRIMARY
        )
        embed.set_footer(text=f"From: {', '.join(choices)}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="reverse", description="Reverse text")
    @app_commands.describe(text="Text to reverse")
    async def reverse(self, interaction: discord.Interaction, text: str):
        """Reverse text"""
        reversed_text = text[::-1]
        
        embed = discord.Embed(
            title="🔄 Reversed Text",
            description=reversed_text,
            color=config.Colors.PRIMARY
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="mock", description="mOcKiNg SpOnGeBoB text")
    @app_commands.describe(text="Text to mock")
    async def mock(self, interaction: discord.Interaction, text: str):
        """Mocking SpongeBob text"""
        mocked = ''.join(
            char.upper() if i % 2 == 0 else char.lower()
            for i, char in enumerate(text)
        )
        
        embed = discord.Embed(
            title="🧽 mOcKiNg SpOnGeBoB",
            description=mocked,
            color=config.Colors.PRIMARY
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="rate", description="Rate something")
    @app_commands.describe(thing="Thing to rate")
    async def rate(self, interaction: discord.Interaction, thing: str):
        """Rate something"""
        # Generate consistent rating based on thing
        rating = (sum(ord(c) for c in thing) % 11)
        
        embed = discord.Embed(
            title="⭐ Rating",
            description=f"I'd rate **{thing}** a **{rating}/10**!",
            color=config.Colors.PRIMARY
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="howgay", description="Calculate gay percentage (joke)")
    @app_commands.describe(user="User to check (optional)")
    async def howgay(
        self,
        interaction: discord.Interaction,
        user: Optional[discord.Member] = None
    ):
        """Gay percentage (joke)"""
        target = user or interaction.user
        percentage = (target.id % 101)
        
        embed = discord.Embed(
            title="🏳️‍🌈 Gay Meter",
            description=f"{target.mention} is **{percentage}%** gay!",
            color=discord.Color.from_rgb(255, 0, 255)
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="pp", description="PP size calculator (joke)")
    @app_commands.describe(user="User to check (optional)")
    async def pp(
        self,
        interaction: discord.Interaction,
        user: Optional[discord.Member] = None
    ):
        """PP size (joke)"""
        target = user or interaction.user
        size = (target.id % 15) + 1
        
        pp = "8" + "=" * size + "D"
        
        embed = discord.Embed(
            title="🍆 PP Size",
            description=f"{target.mention}'s PP:\n`{pp}`\n**{size} inches**",
            color=config.Colors.PRIMARY
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="iq", description="Take a real IQ test")
    async def iq(self, interaction: discord.Interaction):
        """Real IQ test with random questions"""
        await interaction.response.defer()
        
        # Generate random questions
        questions = self._generate_iq_questions()
        
        embed = discord.Embed(
            title="🧠 IQ Test",
            description="Answer 5 questions to determine your IQ!\nYou have 30 seconds per question.",
            color=config.Colors.PRIMARY
        )
        embed.add_field(name="Ready?", value="React with ✅ to start!", inline=False)
        
        msg = await interaction.followup.send(embed=embed)
        await msg.add_reaction("✅")
        
        # Wait for user to start
        def check_start(reaction, user):
            return user == interaction.user and str(reaction.emoji) == "✅" and reaction.message.id == msg.id
        
        try:
            await self.bot.wait_for('reaction_add', timeout=30.0, check=check_start)
        except asyncio.TimeoutError:
            embed.description = "❌ Test cancelled - no response"
            await msg.edit(embed=embed)
            return
        
        # Run the test
        correct = 0
        total = len(questions)
        
        for i, q in enumerate(questions, 1):
            # Show question
            embed = discord.Embed(
                title=f"🧠 IQ Test - Question {i}/{total}",
                description=q['question'],
                color=config.Colors.INFO
            )
            
            # Add options
            options_text = "\n".join([f"{emoji} {opt}" for emoji, opt in zip(['1️⃣', '2️⃣', '3️⃣', '4️⃣'], q['options'])])
            embed.add_field(name="Options:", value=options_text, inline=False)
            embed.set_footer(text="You have 30 seconds to answer")
            
            await msg.clear_reactions()
            await msg.edit(embed=embed)
            
            # Add reaction options
            for emoji in ['1️⃣', '2️⃣', '3️⃣', '4️⃣']:
                await msg.add_reaction(emoji)
            
            # Wait for answer
            def check_answer(reaction, user):
                return user == interaction.user and str(reaction.emoji) in ['1️⃣', '2️⃣', '3️⃣', '4️⃣'] and reaction.message.id == msg.id
            
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check_answer)
                
                # Check if correct
                answer_map = {'1️⃣': 0, '2️⃣': 1, '3️⃣': 2, '4️⃣': 3}
                if answer_map[str(reaction.emoji)] == q['correct']:
                    correct += 1
                    
            except asyncio.TimeoutExpired:
                pass  # No answer = wrong
            
            await asyncio.sleep(0.5)
        
        # Calculate IQ
        percentage = (correct / total) * 100
        base_iq = 85
        iq = int(base_iq + (percentage * 0.6))  # 85-145 range
        
        # Determine category
        if iq < 85:
            category = "Below Average 📉"
            color = config.Colors.ERROR
        elif iq < 100:
            category = "Average 📊"
            color = config.Colors.WARNING
        elif iq < 115:
            category = "Above Average 📈"
            color = config.Colors.SUCCESS
        elif iq < 130:
            category = "Superior 🌟"
            color = config.Colors.PRIMARY
        else:
            category = "Genius! 🧠"
            color = discord.Color.gold()
        
        # Show results
        embed = discord.Embed(
            title="🧠 IQ Test Results",
            description=f"{interaction.user.mention}'s IQ: **{iq}**\n{category}",
            color=color
        )
        embed.add_field(name="Score", value=f"{correct}/{total} correct ({percentage:.0f}%)", inline=False)
        embed.set_footer(text="This is a simplified IQ test for entertainment purposes")
        
        await msg.clear_reactions()
        await msg.edit(embed=embed)
    
    def _generate_iq_questions(self):
        """Generate random IQ test questions"""
        import random
        
        # Pattern recognition questions
        patterns = [
            {
                "question": "What comes next in the sequence?\n2, 4, 8, 16, ?",
                "options": ["24", "32", "20", "28"],
                "correct": 1
            },
            {
                "question": "What comes next in the sequence?\n1, 1, 2, 3, 5, 8, ?",
                "options": ["11", "13", "10", "12"],
                "correct": 1
            },
            {
                "question": "What comes next?\n3, 6, 12, 24, ?",
                "options": ["36", "48", "42", "30"],
                "correct": 1
            },
        ]
        
        # Logic questions
        logic = [
            {
                "question": "If all Bloops are Razzies and all Razzies are Lazzies, then all Bloops are definitely Lazzies?",
                "options": ["True", "False", "Maybe", "Cannot determine"],
                "correct": 0
            },
            {
                "question": "A bat and ball cost $1.10. The bat costs $1 more than the ball. How much does the ball cost?",
                "options": ["$0.10", "$0.05", "$0.15", "$0.20"],
                "correct": 1
            },
        ]
        
        # Math questions
        math = [
            {
                "question": "What is 15% of 200?",
                "options": ["25", "30", "35", "20"],
                "correct": 1
            },
            {
                "question": "If 5 machines make 5 widgets in 5 minutes, how long would it take 100 machines to make 100 widgets?",
                "options": ["100 minutes", "5 minutes", "20 minutes", "10 minutes"],
                "correct": 1
            },
        ]
        
        # Spatial reasoning
        spatial = [
            {
                "question": "How many sides does a hexagon have?",
                "options": ["5", "6", "7", "8"],
                "correct": 1
            },
            {
                "question": "If you fold a square piece of paper in half twice, how many sections do you have?",
                "options": ["2", "3", "4", "8"],
                "correct": 2
            },
        ]
        
        # Combine and shuffle
        all_questions = patterns + logic + math + spatial
        random.shuffle(all_questions)
        
        # Return 5 random questions
        return all_questions[:5]
    
    @app_commands.command(name="simprate", description="Simp rating (joke)")
    @app_commands.describe(user="User to check (optional)")
    async def simprate(
        self,
        interaction: discord.Interaction,
        user: Optional[discord.Member] = None
    ):
        """Simp rating (joke)"""
        target = user or interaction.user
        percentage = (target.id % 101)
        
        if percentage < 25:
            message = "Not a simp 😎"
        elif percentage < 50:
            message = "Slight simp tendencies 🤔"
        elif percentage < 75:
            message = "Certified simp 😳"
        else:
            message = "MEGA SIMP! 🥵"
        
        embed = discord.Embed(
            title="💘 Simp Rating",
            description=f"{target.mention} is **{percentage}%** simp!\n{message}",
            color=discord.Color.from_rgb(255, 105, 180)
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="hack", description="Fake hack someone (joke)")
    @app_commands.describe(user="User to 'hack'")
    async def hack(self, interaction: discord.Interaction, user: discord.Member):
        """Fake hack (joke)"""
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="💻 Hacking...",
            description=f"Target: {user.mention}",
            color=config.Colors.ERROR
        )
        message = await interaction.followup.send(embed=embed)
        
        for hack_msg in HACK_MESSAGES:
            await asyncio.sleep(1.5)
            embed.description = f"Target: {user.mention}\n\n{hack_msg}"
            await message.edit(embed=embed)
        
        # Final message
        embed.title = "✅ Hack Complete!"
        embed.description = f"Successfully hacked {user.mention}!\n\n*This is a joke command. No actual hacking occurred.*"
        embed.color = config.Colors.SUCCESS
        await message.edit(embed=embed)
    
    @app_commands.command(name="mcdonalds", description="Work a shift at McDonald's")
    @app_commands.describe(user="User to make work at McDonald's (optional)")
    async def mcdonalds(
        self,
        interaction: discord.Interaction,
        user: discord.Member = None
    ):
        """Work at McDonald's simulation"""
        target = user or interaction.user
        
        import random
        
        # McDonald's work scenarios
        scenarios = [
            "takes an order for 20 Big Macs and somehow messes it up",
            "accidentally drops fries all over the floor",
            "burns the burgers and sets off the smoke alarm",
            "gets yelled at by Karen for cold fries",
            "cleans the ice cream machine (it's still broken)",
            "works the drive-thru and can't understand anyone",
            "spills a large Coke on a customer",
            "forgets to ask 'would you like fries with that?'",
            "accidentally gives away free food",
            "gets stuck cleaning the bathrooms",
            "has to deal with a customer who wants a refund for eaten food",
            "works a double shift on Black Friday",
            "gets promoted to shift manager (congrats!)",
            "successfully makes 100 burgers without burning any",
            "becomes employee of the month",
            "gets a $0.25 raise after 5 years",
            "quits and becomes a TikTok influencer",
            "starts their own burger restaurant",
            "gets fired for eating too many nuggets",
            "becomes the regional manager"
        ]
        
        # Random earnings (more varied)
        earnings_options = [
            random.randint(25, 75),    # Bad shift
            random.randint(50, 120),   # Normal shift
            random.randint(100, 200),  # Good shift
            random.randint(200, 500),  # Overtime/promotion
            random.randint(1, 10),     # Terrible shift
            random.randint(300, 1000)  # Manager bonus
        ]
        earnings = random.choice(earnings_options)
        
        # Random hours (more varied)
        hours_options = [
            f"{random.randint(1, 3)} hours (sent home early)",
            f"{random.randint(4, 8)} hours",
            f"{random.randint(8, 12)} hours",
            f"{random.randint(12, 16)} hours (double shift)",
            f"{random.randint(16, 24)} hours (triple shift nightmare)",
            "30 minutes (fired immediately)",
            "2 weeks straight (living at McDonald's now)",
            f"{random.randint(1, 12)} hours and {random.randint(1, 59)} minutes"
        ]
        hours = random.choice(hours_options)
        
        # Random scenario
        scenario = random.choice(scenarios)
        
        # Create embed
        embed = discord.Embed(
            title="🍟 McDonald's Work Shift",
            description=f"**{target.display_name}** {scenario}",
            color=0xFFD700  # McDonald's yellow
        )
        
        embed.add_field(
            name="💰 Shift Earnings",
            value=f"${earnings}.00",
            inline=True
        )
        
        embed.add_field(
            name="⏰ Hours Worked",
            value=hours,
            inline=True
        )
        
        # MASSIVE collection of McDonald's dad jokes and funny content
        jokes = [
            "Why did the burger go to therapy? It had too many beefs!",
            "What do you call a nosy pepper at McDonald's? Jalapeño business!",
            "Why don't McDonald's workers ever get cold? They're always by the grill!",
            "What's a McDonald's employee's favorite type of music? Wrap music!",
            "Why did Ronald McDonald go to the doctor? He wasn't feeling very happy!",
            "What do you call a McDonald's worker who can juggle? A Big Mac-robat!",
            "Why don't they serve beer at McDonald's? Because they can't handle the McBurps!",
            "What's the difference between McDonald's and your job? McDonald's actually pays you!",
            "Why did the fries break up with the burger? It was a toxic relationship!",
            "What do you call a McDonald's manager? The Big Boss Mac!",
            "Why is the ice cream machine always broken? It's on a permanent McBreak!",
            "What's Ronald McDonald's favorite day? Fry-day!",
            "Why don't McDonald's employees ever win at poker? They always fold under pressure!",
            "What do you call a McDonald's employee who's also a magician? A McWizard!",
            "Why did the chicken nugget cross the road? To get to the other McSide!",
            "What's the most honest thing at McDonald's? The broken ice cream machine!",
            "Why don't McDonald's burgers ever get lonely? They're always in a bun-dle!",
            "What do you call a McDonald's worker's favorite movie? The Fast and the McFurious!",
            "Why did the Happy Meal cry? It wasn't feeling so happy!",
            "What's a McDonald's worker's favorite subject? Fry-ology!",
            "Why don't McDonald's employees ever get lost? They always know where the golden arches are!",
            "What do you call a McDonald's worker who tells jokes? A McComedian!",
            "Why did the milkshake go to school? To get a little shake-ucation!",
            "What's Ronald McDonald's favorite exercise? The Big Mac-attack!",
            "Why don't McDonald's workers ever get tired? They're always on a roll!",
            "What do you call a McDonald's worker's pet? A Ham-burger!",
            "Why did the apple pie go to the dentist? It needed a filling!",
            "What's a McDonald's worker's favorite game? Pickle ball!",
            "Why don't McDonald's employees ever get speeding tickets? They're always in the slow lane!",
            "What do you call a McDonald's worker who's also a detective? Sherlock Fries!",
            "Why did the ketchup packet break up with the mustard? It was too saucy!",
            "What's Ronald McDonald's favorite type of math? Burger-nometry!",
            "Why don't McDonald's workers ever get sunburned? They're always under the heat lamps!",
            "What do you call a McDonald's worker who's also a superhero? Captain McAmerica!",
            "Why did the French fry go to therapy? It had too much salt in its life!",
            "What's a McDonald's worker's favorite dance? The McShuffle!",
            "Why don't McDonald's employees ever get locked out? They always have the golden keys!",
            "What do you call a McDonald's worker who's also a musician? A McRapper!",
            "Why did the Big Mac go to the gym? To work on its buns!",
            "What's Ronald McDonald's favorite social media? McInstagram!",
            "Why don't McDonald's workers ever get cold feet? They're always near the fryer!",
            "What do you call a McDonald's worker who's also a teacher? Professor McEducation!",
            "Why did the chicken sandwich cross the playground? To get to the other slide!",
            "What's a McDonald's worker's favorite holiday? Fry-day the 13th!",
            "Why don't McDonald's employees ever get stage fright? They're used to performing under pressure!",
            "What do you call a McDonald's worker who's also a pilot? Captain McFly!",
            "Why did the hash brown go to college? To get hash-educated!",
            "What's Ronald McDonald's favorite weather? When it's raining cats and McFlurries!",
            "Why don't McDonald's workers ever get homesick? Because McDonald's is everywhere!",
            "What do you call a McDonald's worker who's also a gardener? A McFarmer!"
        ]
        
        embed.add_field(
            name="😂 McDonald's Dad Joke",
            value=random.choice(jokes),
            inline=False
        )
        
        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/3/36/McDonald%27s_Golden_Arches.svg")
        embed.set_footer(text="I'm lovin' it! 🍟")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot))
