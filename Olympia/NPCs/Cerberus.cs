using Microsoft.Xna.Framework;
using Terraria;
using Terraria.Audio;
using Terraria.GameContent.ItemDropRules;
using Terraria.ID;
using Terraria.ModLoader;

namespace Olympia.NPCs
{
    [AutoloadBossHead]
    public class Cerberus : ModNPC
    {
        private int hoverTimer;

        public override void SetStaticDefaults()
        {
            Main.npcFrameCount[Type] = 4;
            NPCID.Sets.MPAllowedEnemies[Type] = true;
        }

        public override void SetDefaults()
        {
            NPC.width = 110;
            NPC.height = 80;
            NPC.damage = 44;
            NPC.defense = 14;
            NPC.lifeMax = 5200;
            NPC.HitSound = SoundID.NPCHit54;
            NPC.DeathSound = SoundID.NPCDeath6;
            NPC.knockBackResist = 0f;
            NPC.value = Item.buyPrice(gold: 8);
            NPC.aiStyle = -1;
            NPC.noGravity = false;
            NPC.noTileCollide = false;
            NPC.boss = true;
            NPC.npcSlots = 10f;
            NPC.lavaImmune = true;
            Music = MusicID.Boss2;
        }

        public override void ApplyDifficultyAndPlayerScaling(int numPlayers, float balance, float bossAdjustment)
        {
            NPC.lifeMax = (int)(NPC.lifeMax * 0.75f * bossAdjustment);
            NPC.damage = (int)(NPC.damage * 0.75f);
        }

        private void ToHover()
        {
            NPC.ai[0] = 0f;
            NPC.ai[1] = 0f;
            NPC.ai[2] = 0f;
        }

        public override void AI()
        {
            NPC.TargetClosest(true);
            Player target = Main.player[NPC.target];
            if (!target.active || target.dead)
            {
                NPC.velocity.X *= 0.9f;
                NPC.EncourageDespawn(60);
                return;
            }
            bool enraged = NPC.life < NPC.lifeMax * 0.5f;
            int dir = target.Center.X > NPC.Center.X ? 1 : -1;
            ref float state = ref NPC.ai[0];
            ref float timer = ref NPC.ai[1];
            ref float count = ref NPC.ai[2];
            timer++;
            NPC.spriteDirection = dir;
            switch ((int)state)
            {
                default:
                case 0: // walk at the player, jumping what is in the way, then choose an attack
                {
                    NPC.velocity.X = MathHelper.Lerp(NPC.velocity.X, dir * 4.4f * (enraged ? 1.3f : 1f), 0.08f);
                    if (NPC.collideX && NPC.velocity.Y == 0f)
                    {
                        NPC.velocity.Y = -10.0f;
                    }
                    if (timer > (enraged ? 60f : 100f))
                    {
                        timer = 0f;
                        count = 0f;
                        switch (Main.rand.Next(3))
                        {
                            case 0: state = 1f; break; case 1: state = 2f; break; case 2: state = 3f; break;
                        }
                    }
                    break;
                }
                case 1: // a charge: a telegraph, then a rush along the ground, again and again
                {
                    if (timer < 30f)
                    {
                        NPC.velocity.X *= 0.8f;
                    }
                    else if (timer == 30f)
                    {
                        NPC.velocity.X = dir * 15.0f * (enraged ? 1.25f : 1f);
                        SoundEngine.PlaySound(SoundID.Roar, NPC.Center);
                    }
                    else if (timer > 30f && NPC.collideX && NPC.velocity.Y == 0f)
                    {
                        NPC.velocity.Y = -10.0f;
                    }
                    if (timer > 80f)
                    {
                        count++;
                        timer = 0f;
                        if (count >= 4f)
                        {
                            ToHover();
                        }
                    }
                    break;
                }
                case 2: // a leap and a slam: debris thrown out on landing
                {
                    if (timer == 1f)
                    {
                        NPC.velocity = new Vector2(dir * 5f, -13f);
                    }
                    else if (timer > 20f && NPC.velocity.Y == 0f)
                    {
                        if (Main.netMode != NetmodeID.MultiplayerClient)
                        {
                            int n = 9 + (enraged ? 3 : 0);
                            for (int i = 0; i < n; i++)
                            {
                                float ang = MathHelper.Pi * (0.1f + 0.8f * i / System.Math.Max(1, n - 1));
                                Vector2 vel = new Vector2((float)System.Math.Cos(ang), -(float)System.Math.Sin(ang)) * 10.0f;
                                Projectile.NewProjectile(NPC.GetSource_FromAI(), NPC.Bottom, vel, ModContent.ProjectileType<Projectiles.StompDebris>(), 30, 0f, Main.myPlayer);
                            }
                        }
                        SoundEngine.PlaySound(SoundID.Item14, NPC.Center);
                        ToHover();
                    }
                    break;
                }
                case 3: // a summons
                {
                    NPC.velocity.X *= 0.9f;
                    if (timer == 30f && Main.netMode != NetmodeID.MultiplayerClient)
                    {
                        int minions = 2 + (enraged ? 1 : 0);
                        for (int i = 0; i < minions; i++)
                        {
                            NPC.NewNPC(NPC.GetSource_FromAI(), (int)NPC.Center.X + (i - minions / 2) * 40, (int)NPC.Center.Y, ModContent.NPCType<NPCs.Hoplite>());
                        }
                        SoundEngine.PlaySound(SoundID.Item8, NPC.Center);
                    }
                    if (timer > 70f)
                    {
                        ToHover();
                    }
                    break;
                }
            }
        }

        public override void FindFrame(int frameHeight)
        {
            NPC.frameCounter++;
            if (NPC.frameCounter > 7)
            {
                NPC.frameCounter = 0;
                NPC.frame.Y = (NPC.frame.Y + frameHeight) % (frameHeight * Main.npcFrameCount[Type]);
            }
        }

        public override void ModifyNPCLoot(NPCLoot npcLoot)
        {
            npcLoot.Add(ItemDropRule.BossBag(ModContent.ItemType<Items.CerberusBag>()));
            LeadingConditionRule notExpert = new LeadingConditionRule(new Conditions.NotExpert());
            notExpert.OnSuccess(ItemDropRule.Common(ModContent.ItemType<Items.ChainsOfHades>(), 1, 1, 1));
            notExpert.OnSuccess(ItemDropRule.Common(ModContent.ItemType<Items.HellfangBlade>(), 2, 1, 1));
            notExpert.OnSuccess(ItemDropRule.Common(ModContent.ItemType<Items.CerberusFang>(), 1, 8, 14));
            npcLoot.Add(notExpert);
        }

        public override void OnKill()
        {
            Systems.OlympiaWorld.downedCerberus = true;
            if (Main.netMode == NetmodeID.Server)
            {
                NetMessage.SendData(MessageID.WorldData);
            }
        }
    }
}
