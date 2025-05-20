class Balls(commands.GroupCog, group_name=settings.players_group_cog_name):
    """
    View and manage your countryballs collection.
    """

    def __init__(self, bot: "BallsDexBot"):
        self.bot = bot
        self.secret_codes = ["code1", "code2", "code3", "code4", "code5"]  # Change the codes or add more
        self.redeemed_codes = self.load_redeemed_codes()  
        logging.basicConfig(level=logging.INFO)

    def load_redeemed_codes(self):
        """Loads redeemed codes from a JSON file."""
        if os.path.exists("redeemed_codes.json"):
            with open("redeemed_codes.json", "r") as f:
                return json.load(f)
        return {}  

    def save_redeemed_codes(self):
        """Guarda los códigos canjeados en un archivo JSON."""
        with open("redeemed_codes.json", "w") as f:
            json.dump(self.redeemed_codes, f)

    @app_commands.command()
    async def code(self, interaction: discord.Interaction, code: str):
        """
        redeem a code for a ball

        Parameters
        ----------
        code: str
            The code that the user wants to verify.
        """
        player_id = str(interaction.user.id)  
        
        if code in self.secret_codes:
            if player_id in self.redeemed_codes and code in self.redeemed_codes[player_id]:
                await interaction.response.send_message("You have already redeemed this code before.", ephemeral=True)
                return
            
            active_balls = [ball for ball in balls.values() if ball.enabled]
            if not active_balls:
                await interaction.response.send_message("No balls available.", ephemeral=True)
                return
            
            random_ball = random.choice(active_balls)
            try:
                player = await Player.get(discord_id=interaction.user.id)
                await BallInstance.create(player=player, ball=random_ball)
                
                if player_id not in self.redeemed_codes:
                    self.redeemed_codes[player_id] = []
                self.redeemed_codes[player_id].append(code)
                
                self.save_redeemed_codes()
                
                await interaction.response.send_message(f"Congratulations! You've received {random_ball.country} !!!", ephemeral=True)
                logging.info(f"User  {player_id} redeemed code '{code}' and received {random_ball.country}.")
            except Exception as e:
                logging.error(f"Error while redeeming code for user {player_id}: {e}")
                await interaction.response.send_message("An error occurred, try again later.", ephemeral=True)
        else:
            await interaction.response.send_message("The code is not valid.", ephemeral=True)
