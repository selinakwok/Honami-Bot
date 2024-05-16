import sqlite3
import discord
import os
import datetime
import re
import sys
import random
import json

from dotenv import load_dotenv
from discord.ext import commands
from discord.ui import View
from discord.ext import tasks

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='$', intents=intents)
con = sqlite3.connect("reminders.db")
cur = con.cursor()


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    today = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
    today = today.strftime("%H:%M:%S")
    print(today)
    reminder.start()
    await bot.change_presence(activity=discord.Game("霽れを待つ / $honami"))


reminder_messages = [
    "別睡了 你5分鐘後有事要做 <:ln_hnm_sorry:1015609265035161650>",
    "請準備做5分鐘後的事情 <:ln_hnm_congratulations:1011506760080695327>",
    "溫馨提示: 你5分鐘後的有事情要做 <:ln_hnm_smile:1024341146878611496>",
    "5分鐘後的節目 你準備好了嗎 <:ln_hnm_fufufu:1011536521469366292>",
    "5分鐘後不做你該做的東西 志步會罵你 <:ln_hnm_yabe:1006484419126767626>",
    "記得5分鐘後出現 咲希等著跟你玩 <:ln_hnm_speechless:1011536500141338654>",
    "5分鐘後不出現 真冬學姐會塞你進魚缸 <:ln_hnm_yabe:1006484419126767626>",
    "約好了5分鐘後一起上車頂看星星 對吧 <:ln_hnm_smile:1024341146878611496>",
    "你5分鐘後不做該做的事情就變鴿子了 <:ln_hnm_yabe:1006484419126767626>",
    "你5分鐘後不過來我就不給你蘋果派了 <:ln_hnm_speechless:1011536500141338654>",
    "蘋果派在5分鐘後會賣光 <:ln_hnm_yabe:1006484419126767626>"
]

refill_ids = []
bot.reminder_ids = []
bot.reminder_msg_id = 0


async def button_callback(interaction):
    uid = interaction.user.id
    dt = interaction.original_response
    print(dt)
    dt = interaction.data["custom_id"]
    try:
        event = cur.execute("SELECT event_dt, event_desc FROM archive WHERE uid = :uid AND event_dt = :dt",
                            {"uid": uid, "dt": dt})
        event = event.fetchone()
        print_dt = event[0]
        print_dt = datetime.datetime.strptime(print_dt, "%m%d%H%M") + datetime.timedelta(minutes=5)
        print_dt = print_dt.strftime("%m/%d %H%M")
        desc = event[1]
        await interaction.response.send_message(print_dt + " :  " + desc +
                                                " <:ln_hnm_congratulations:1011506760080695327>", ephemeral=True)
    except TypeError:
        await interaction.response.send_message("你這個時段沒有提醒事項 <:ln_hnm_speechless:1011536500141338654>",
                                                ephemeral=True)


@tasks.loop(seconds=1)
async def reminder():
    now_dt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
    now_dt = now_dt.strftime("%m%d%H%M%S")

    dts = cur.execute("SELECT DISTINCT dt FROM reminders")
    dts = dts.fetchall()
    dts = [dt[0] + "00" for dt in dts]

    melt = cur.execute("SELECT DISTINCT dt FROM melt")
    melt = melt.fetchall()
    melt = [m[0] for m in melt]

    shrimp = cur.execute("SELECT DISTINCT dt FROM shrimp")
    shrimp = shrimp.fetchall()
    shrimp = [m[0] for m in shrimp]

    # ----- 消體報班 -----
    if now_dt.endswith("215700"):
        reminder_2157_members = []
        channel = bot.get_channel(1029506502312087582)
        guild = bot.get_guild(1006236899570110614)
        role = guild.get_role(1029703649749893160)

        for user in guild.members:
            if role in user.roles:
                reminder_2157_members.append(user.id)

        if not reminder_2157_members:
            pass
        else:
            reminder_2157_message = ""
            for uid in reminder_2157_members:
                mention = "<@" + str(uid) + ">"
                reminder_2157_message = reminder_2157_message + " " + mention
            await channel.send(
                reminder_2157_message + "\n3分鐘後要在 <#1006446844995444807> 報班了<:ln_hnm_fufufu:1011536521469366292>")

    # ----- 換日 -----
    if now_dt.endswith("000000"):
        bot.reminder_ids = []
        channel = bot.get_channel(1029506502312087582)
        guild = bot.get_guild(1006236899570110614)
        role = guild.get_role(1029704053665570836)
        for user in guild.members:
            if role in user.roles:
                bot.reminder_ids.append(user.id)

        if not bot.reminder_ids:
            pass
        else:
            reminder_0000_message = ""
            for uid in bot.reminder_ids:
                mention = "<@" + str(uid) + ">"
                reminder_0000_message = reminder_0000_message + " " + mention
            reminder_msg = await channel.send(
                reminder_0000_message + "\n換日了 記得要打挑戰/買體力包喔 <:ln_hnm_congratulations:1011506760080695327>")
            bot.reminder_msg_id = reminder_msg.id
            reaction = bot.get_emoji(1082662447569186816)
            await reminder_msg.add_reaction(reaction)

    if now_dt.endswith("010000") or now_dt.endswith("020000") or now_dt.endswith("030000") or now_dt.endswith(
            "033000") or now_dt.endswith("034500") or now_dt.endswith("035000") or now_dt.endswith(
            "035500") or now_dt.endswith("035800"):
        channel = bot.get_channel(1029506502312087582)
        reminder_msg = await channel.fetch_message(bot.reminder_msg_id)
        for r in reminder_msg.reactions:
            async for user in r.users():
                if user.id in bot.reminder_ids:
                    bot.reminder_ids.remove(user.id)
        if not bot.reminder_ids:
            pass
        else:
            reminder_message = ""
            for uid in bot.reminder_ids:
                mention = "<@" + str(uid) + ">"
                reminder_message = reminder_message + " " + mention
            if now_dt.endswith("035800"):
                await channel.send(
                    reminder_message + "\n最後機會 還不打挑戰就沒了 <:ln_hnm_yabe:1006484419126767626>")
            else:
                await channel.send(
                    reminder_message + "\n快去打挑戰/買體力包 <:ln_hnm_speechless:1011536500141338654>")

    # ----- reminder times -----
    if now_dt in dts:
        print("initiate reminder for " + now_dt)
        uids = cur.execute("SELECT uid FROM reminders WHERE dt = :now_dt",
                           {"now_dt": now_dt[:-2]})
        uids = uids.fetchall()
        uids = ["<@" + uid[0] + ">" for uid in uids]
        message = ""
        for mention in uids:
            message = message + " " + mention

        channel = bot.get_channel(1029506502312087582)
        message_choice = random.SystemRandom().choice(reminder_messages)

        button = discord.ui.Button(label="你的提醒事項",
                                   custom_id=now_dt[:-2],
                                   emoji="<:ln_hnm_oh:1011638141364473866>")
        reminder_view = View()
        reminder_view.add_item(button)

        await channel.send(message + "\n" + message_choice, view=reminder_view)
        button.callback = button_callback

        # delete from databases
        cur.execute("DELETE FROM user WHERE event_dt = :dt",
                    {"dt": now_dt[:-2]})
        con.commit()
        cur.execute("DELETE FROM reminders WHERE dt = :dt",
                    {"dt": now_dt[:-2]})
        con.commit()

    # ----- 消體車提醒 -----
    if now_dt in melt:
        print("消體車: initiate reminder for " + now_dt)
        mids = cur.execute("SELECT mid FROM melt WHERE dt = :now_dt",
                           {"now_dt": now_dt})
        mids = mids.fetchall()
        mids = [m[0] for m in mids]
        if mids:
            for mid in mids:
                uids = cur.execute("SELECT uid FROM meltUsers WHERE mid = :mid",
                                   {"mid": mid})
                uids = uids.fetchall()
                uids = [uid[0] for uid in uids]

                """users = []
                not_registered = ""
                for u in uids:
                    skill = cur.execute("SELECT skill FROM bigFace WHERE uid = :uid",
                                        {"uid": u})
                    skill = skill.fetchone()
                    if skill:
                        skill = skill[0]
                    else:
                        skill = 2.5
                        not_registered = "\n<:0_sacabambaspis:1125767872476610570> 站位未確認: 有人沒用`$laf_r`登記跑隊倍率 <:ln_hnm_sorry:1015609265035161650>"
                    users.append([u, skill])
                users.sort(key=lambda x: x[1], reverse=True)"""

                uids = ["<@" + u + ">" for u in uids]
                message = ""
                for mention in uids:
                    message = message + " " + mention

                """# order = ['', '', '', '', '']
                full = ""
                if len(uids) == 5:
                    order[0] = uids[4]
                    order[1] = uids[1]
                    order[2] = uids[0]
                    order[3] = uids[2]
                    order[4] = uids[3]
                    for mention in order:
                        message = message + " " + mention
                else:
                    for mention in uids:
                        message = message + " " + mention
                    full = "\n<:0_sacabambaspis:1125767872476610570> 人數!=5 確認上車成員後可使用`$laf`查看大臉站位 <:ln_hnm_speechless:1011536500141338654>"""

                carNo = cur.execute("SELECT cno FROM melt WHERE dt = :now_dt AND mid = :mid",
                                    {"now_dt": now_dt, "mid": mid})
                carNo = carNo.fetchone()[0]
                if carNo == 1:
                    channel = bot.get_channel(1009137745886728202)
                elif carNo == 2:
                    channel = bot.get_channel(1009138587834515577)
                elif carNo == 3:
                    channel = bot.get_channel(1039853879237545994)
                elif carNo == 4:
                    channel = bot.get_channel(1042186978579447829)
                else:
                    channel = bot.get_channel(1009137745886728202)

                melt_message = await channel.send(
                    message + "\n記得5分鐘後要消體 <:ln_hnm_congratulations:1011506760080695327>\n(請按反應簽到 <:ln_hnm_fufufu:1011536521469366292>)")
                emoji = bot.get_emoji(1011536521469366292)
                await melt_message.add_reaction(emoji)

    # shrimp
    if now_dt in shrimp:
        print("拍蝦車: initiate reminder for " + now_dt)
        mids = cur.execute("SELECT mid FROM shrimp WHERE dt = :now_dt",
                           {"now_dt": now_dt})
        mids = mids.fetchall()
        mids = [m[0] for m in mids]
        if mids:
            for mid in mids:
                uids = cur.execute("SELECT uid FROM shrimpUsers WHERE mid = :mid",
                                   {"mid": mid})
                uids = uids.fetchall()
                uids = ["<@" + uid[0] + ">" for uid in uids]
                if uids:
                    message = ""
                    for mention in uids:
                        message = message + " " + mention
                    channel = bot.get_channel(1055586909776252938)
                    shrimp_message = await channel.send(
                        message + "\n5分鐘後來拍蝦 <a:slapshrimp:1120737597979893810> <a:ln_hnm_pet:1082662447569186816>"
                                  "\n(請按反應簽到 <:ln_hnm_fufufu:1011536521469366292>)")
                    emoji = bot.get_emoji(1011536521469366292)
                    await shrimp_message.add_reaction(emoji)

    # ----- refill reminder -----
    if now_dt[-4:] in ["0000", "0200", "0400", "0600", "0800", "1000", "1200", "1400", "1600", "1800", "2000",
                       "2200", "2400", "2600", "2800", "3000", "3200", "3400", "3600", "3800", "4000",
                       "4200", "4400", "4600", "4800", "5000", "5200", "5400", "5600", "5800"]:
        if len(refill_ids) != 0:
            mentions = ""
            for i in refill_ids:
                mentions = mentions + " " + i
            channel = bot.get_channel(1029506502312087582)
            await channel.send(
                mentions + "<:ln_hnm_congratulations:1011506760080695327> 記得回體 <:z_livebonus:1006937417900642426>")


@bot.event
async def on_message(message):
    if message.channel.id not in [1006446844995444807, 1120707069268480110, 1007203228515057687]:
        await bot.process_commands(message)
        return
    dt_format = re.match("[0-9]{1,2}/[0-9]{1,2} [0-9]{4} .+", message.content)
    dt_match = bool(dt_format)
    if not dt_match:
        await bot.process_commands(message)
        return

    car = re.split(" ", message.content)
    c_date = re.split("/", car[0])

    if int(car[1][0:2]) > 23:
        await message.reply("Hour cannot be >23 <:ln_hnm_speechless:1011536500141338654>", delete_after=10)
        await message.delete()
        return

    c_dt = c_date[0].zfill(2) + c_date[1].zfill(2) + car[1] + "00"  # format: 0416203000
    r_dt = datetime.datetime.strptime(c_dt, "%m%d%H%M%S") - datetime.timedelta(minutes=5)
    r_dt = r_dt.strftime("%m%d%H%M%S")  # format: 0416202500

    # melt
    if message.channel.id in [1006446844995444807, 1007203228515057687]:
        cars_dt = cur.execute("SELECT dt FROM melt WHERE dt = :dt",
                              {"dt": r_dt})
        cars_dt = cars_dt.fetchall()
        if cars_dt:
            cars_dt = [c[0] for c in cars_dt]
            cno = len(cars_dt) + 1
        else:
            cno = 1
        cur.execute("INSERT INTO melt(mid, dt, driver, cno) VALUES(?,?,?,?)",
                    (message.id, r_dt, message.author.id, cno))
        con.commit()

    # shrimp
    else:
        cno = 1
        cur.execute("INSERT INTO shrimp(mid, dt, driver, cno) VALUES(?,?,?,?)",
                    (message.id, r_dt, message.author.id, cno))
        con.commit()

    """cars_dt = cur.execute("SELECT dt FROM melt")
    cars_dt = cars_dt.fetchall()
    cars_dt = [c[0] for c in cars_dt]

    dt_in_range = []
    for c in cars_dt:
        dt = datetime.datetime.strptime(c, "%m%d%H%M%S")
        diff = dt - r_dt
        if diff.total_seconds()/60 <= 30:
            dt_in_range.append(dt)

    r_dt = r_dt.strftime("%m%d%H%M%S")
    cur.execute("INSERT INTO melt(mid, dt, driver, cno) VALUES(?,?,?,?)",
                (message.id, r_dt, message.author.id, 1))
    con.commit()

    if dt_in_range:
        r_dt = datetime.datetime.strptime(r_dt, "%m%d%H%M%S")
        dt_in_range.append(r_dt)
        dt_in_range.sort()
        print(dt_in_range)

        cno = 1
        for dt in set(dt_in_range):
            dt_str = dt.strftime("%m%d%H%M%S")
            dt_mid = cur.execute("SELECT mid FROM melt WHERE dt = :dt",
                                 {"dt": dt_str})
            dt_mid = dt_mid.fetchall()
            dt_mid = [mid[0] for mid in dt_mid]
            for mid in dt_mid:
                cur.execute("UPDATE melt set cno = ? WHERE mid = ?",
                            (cno, mid))
                con.commit()
                cno += 1"""

    await bot.process_commands(message)


@bot.event
async def on_raw_reaction_add(payload):
    # validation: if reaction is on 報班 message
    if payload.channel_id not in [1006446844995444807, 1120707069268480110, 1007203228515057687]:
        return
    res = cur.execute("SELECT mid FROM melt")
    res = res.fetchall()
    res = [r[0] for r in res]
    shrimp = cur.execute("SELECT mid FROM shrimp")
    shrimp = shrimp.fetchall()
    shrimp = [r[0] for r in shrimp]
    if str(payload.message_id) not in res and str(payload.message_id) not in shrimp:
        return
    if str(payload.emoji) == "<:z_livebonus:1006937417900642426>":
        return

    # melt
    if payload.channel_id in [1006446844995444807, 1007203228515057687]:
        c_name = payload.member.nick.rsplit("(", 1)[0] + "(" + payload.member.name + ")"
        c_record = cur.execute("SELECT record from melt where mid = :mid",
                               {"mid": payload.message_id})
        c_record = c_record.fetchone()[0]
        if c_record:
            c_record = json.loads(c_record)
            c_record.append("+ " + c_name + " " + str(payload.emoji))
        else:
            c_record = ["+ " + c_name + " " + str(payload.emoji)]
        c_record = json.dumps(c_record)
        cur.execute("UPDATE melt SET record = ? WHERE mid = ?",
                    (c_record, payload.message_id))
        con.commit()

        rxn = cur.execute("SELECT * FROM meltUsers WHERE mid = :mid AND uid = :uid",
                          {"mid": payload.message_id, "uid": payload.user_id})
        rxn = rxn.fetchone()
        if not rxn:
            cur.execute("INSERT INTO meltUsers VALUES(?,?)",
                        (payload.message_id, payload.user_id))

    # shrimp
    else:
        c_name = payload.member.nick.rsplit("(", 1)[0] + "(" + payload.member.name + ")"
        c_record = cur.execute("SELECT record from shrimp where mid = :mid",
                               {"mid": payload.message_id})
        c_record = c_record.fetchone()[0]
        if c_record:
            c_record = json.loads(c_record)
            c_record.append("+ " + c_name + " " + str(payload.emoji))
        else:
            c_record = ["+ " + c_name + " " + str(payload.emoji)]
        c_record = json.dumps(c_record)
        cur.execute("UPDATE shrimp SET record = ? WHERE mid = ?",
                    (c_record, payload.message_id))
        con.commit()

        rxn = cur.execute("SELECT * FROM shrimpUsers WHERE mid = :mid AND uid = :uid",
                          {"mid": payload.message_id, "uid": payload.user_id})
        rxn = rxn.fetchone()
        if not rxn:
            cur.execute("INSERT INTO shrimpUsers VALUES(?,?)",
                        (payload.message_id, payload.user_id))


@bot.event
async def on_raw_reaction_remove(payload):
    if payload.channel_id not in [1006446844995444807, 1120707069268480110, 1007203228515057687]:
        return
    res = cur.execute("SELECT mid FROM melt")
    res = res.fetchall()
    res = [r[0] for r in res]
    shrimp = cur.execute("SELECT mid FROM shrimp")
    shrimp = shrimp.fetchall()
    shrimp = [r[0] for r in shrimp]
    if str(payload.message_id) not in res and str(payload.message_id) not in shrimp:
        return
    if str(payload.emoji) == "<:z_livebonus:1006937417900642426>":
        return

    c_name = await bot.get_guild(1006236899570110614).fetch_member(payload.user_id)
    c_name = c_name.nick.rsplit("(", 1)[0] + "(" + c_name.name + ")"

    # melt
    if payload.channel_id in [1006446844995444807, 1007203228515057687]:
        c_record = cur.execute("SELECT record from melt where mid = :mid",
                               {"mid": payload.message_id})
        c_record = c_record.fetchone()[0]
        c_record = json.loads(c_record)
        c_record.append("- " + c_name + " " + str(payload.emoji))
        c_record = json.dumps(c_record)
        cur.execute("UPDATE melt SET record = ? WHERE mid = ?",
                    (c_record, payload.message_id))
        con.commit()

        reactors = []
        message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        for r in message.reactions:
            async for user in r.users():
                reactors.append(user.id)
        if payload.user_id not in reactors:
            cur.execute("DELETE FROM meltUsers WHERE mid = :mid AND uid = :uid",
                        {"mid": payload.message_id, "uid": payload.user_id})
            con.commit()
            print("deleted reaction user from meltUsers")

    # shrimp
    else:
        c_record = cur.execute("SELECT record from shrimp where mid = :mid",
                               {"mid": payload.message_id})
        c_record = c_record.fetchone()[0]
        c_record = json.loads(c_record)
        c_record.append("- " + c_name + " " + str(payload.emoji))
        c_record = json.dumps(c_record)
        cur.execute("UPDATE shrimp SET record = ? WHERE mid = ?",
                    (c_record, payload.message_id))
        con.commit()

        reactors = []
        message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        for r in message.reactions:
            async for user in r.users():
                reactors.append(user.id)
        if payload.user_id not in reactors:
            cur.execute("DELETE FROM shrimpUsers WHERE mid = :mid AND uid = :uid",
                        {"mid": payload.message_id, "uid": payload.user_id})
            con.commit()
            print("deleted reaction user from shrimpUsers")

    car_author = message.author.id
    notify_members = []
    guild = bot.get_guild(1006236899570110614)
    role = guild.get_role(1043345953589055498)
    for user in guild.members:
        if role in user.roles:
            notify_members.append(user.id)
    if car_author not in notify_members:
        return
    else:
        if payload.channel_id in [1006446844995444807, 1007203228515057687]:
            thread = bot.get_channel(1043337218367955055)
        else:
            thread = bot.get_channel(1120739844444913715)
        await thread.send("<@" + str(car_author) + ">\n<@" + str(payload.user_id) + "> 退了 `" + message.content + "`")


@bot.event
async def on_raw_message_delete(payload):
    if payload.channel_id not in [1006446844995444807, 1120707069268480110, 1007203228515057687]:
        return

    # melt
    if payload.channel_id in [1006446844995444807, 1007203228515057687]:
        mid_list = cur.execute("SELECT mid FROM melt")
        mid_list = [m[0] for m in mid_list.fetchall()]
        if str(payload.message_id) in mid_list:
            cur.execute("DELETE FROM melt WHERE mid = :mid",
                        {"mid": str(payload.message_id)})
            con.commit()
            cur.execute("DELETE FROM meltUsers WHERE mid = :mid",
                        {"mid": str(payload.message_id)})
            con.commit()

    # shrimp
    else:
        mid_list = cur.execute("SELECT mid FROM shrimp")
        mid_list = [m[0] for m in mid_list.fetchall()]
        if str(payload.message_id) in mid_list:
            cur.execute("DELETE FROM shrimp WHERE mid = :mid",
                        {"mid": str(payload.message_id)})
            con.commit()
            cur.execute("DELETE FROM shrimpUsers WHERE mid = :mid",
                        {"mid": str(payload.message_id)})
            con.commit()


@bot.command(aliases=['r'])
async def record(ctx, url):
    mid = url.rsplit("/", 1)[1]
    if mid[-1] == ">":
        mid = mid[:-1]

    res = cur.execute("SELECT mid FROM melt")
    res = res.fetchall()
    res = [r[0] for r in res]
    if str(mid) in res:
        car = cur.execute("SELECT * FROM melt WHERE mid = :mid",
                          {"mid": mid})
        car = car.fetchone()[4]
        record_str = ""
        if car:
            c_record = json.loads(car)
            for r in c_record:
                record_str = record_str + "\n" + r
        else:
            record_str = "暫無報班紀錄"

        c_desc = bot.get_channel(1006446844995444807)
        c_desc = await c_desc.fetch_message(int(mid))
        c_desc = c_desc.content
        embed = discord.Embed(title="報班紀錄:\n" + c_desc,
                              description=record_str,
                              colour=0xed6565)

        c_info = cur.execute("SELECT * FROM melt WHERE mid = :mid",
                             {"mid": mid})
        c_driver = c_info.fetchone()[2]
        c_driver = bot.get_user(int(c_driver))
        c_driver = c_driver.name
        c_info = cur.execute("SELECT * FROM melt WHERE mid = :mid",
                             {"mid": mid})
        c_no = c_info.fetchone()[3]
        embed.set_footer(text="車主: " + c_driver + " | 車號: " + str(c_no))
        await ctx.send(embed=embed)

    # shrimp
    else:
        res = cur.execute("SELECT mid FROM shrimp")
        res = res.fetchall()
        res = [r[0] for r in res]
        if str(mid) in res:
            car = cur.execute("SELECT * FROM shrimp WHERE mid = :mid",
                              {"mid": mid})
            car = car.fetchone()[4]
            record_str = ""
            if car:
                c_record = json.loads(car)
                for r in c_record:
                    record_str = record_str + "\n" + r
            else:
                record_str = "暫無報班紀錄"

            c_desc = bot.get_channel(1120707069268480110)
            c_desc = await c_desc.fetch_message(int(mid))
            c_desc = c_desc.content
            embed = discord.Embed(title="報班紀錄:\n" + c_desc,
                                  description=record_str,
                                  colour=0xed6565)

            c_info = cur.execute("SELECT * FROM shrimp WHERE mid = :mid",
                                 {"mid": mid})
            c_driver = c_info.fetchone()[2]
            c_driver = bot.get_user(int(c_driver))
            c_driver = c_driver.name
            c_info = cur.execute("SELECT * FROM shrimp WHERE mid = :mid",
                                 {"mid": mid})
            c_no = c_info.fetchone()[3]
            embed.set_footer(text="車主: " + c_driver + " | 車號: " + str(c_no))
            await ctx.send(embed=embed)
        else:
            await ctx.send("Car does not exist <:ln_hnm_yabe:1006484419126767626>")
            return


def convert(event):
    input = re.split(" ", event, maxsplit=2)  # a: [1/31, 2330, desc], d: [1/31, 2330]
    if not bool(re.fullmatch("[0-9][0-9]?/[0-9][0-9]?", input[0])):
        return "invalid_date_format"
    if not bool(re.fullmatch("[0-9]{4}", input[1])):
        return "invalid_time_format"

    date = re.split("/", input[0])
    year = datetime.datetime.now().year
    month = date[0]
    day = date[1]
    hr = input[1][0:2]
    min = input[1][2:4]

    # check if datetime is valid
    try:
        reminder_dt = datetime.datetime(int(year), int(month), int(day), int(hr), int(min),
                                        tzinfo=datetime.timezone.utc) - datetime.timedelta(minutes=5)
    except ValueError:
        error_type = sys.exc_info()[0]
        error_message = sys.exc_info()[1]
        return error_type, error_message

    # check if reminder dt has passed
    if reminder_dt < datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8):
        error = "dtPassed"
        return error

    reminder_dt = reminder_dt.strftime("%m%d%H%M")
    if len(input) == 2:
        return reminder_dt
    else:
        return reminder_dt, input[2]


@bot.command(name="a",
             brief="新加提醒事項",
             help="新加提醒事項"
                  "\n- events: 新增事項的日期、時間和内容"
                  "\n格式爲 mm/dd HHMM 内容[, mm/dd HHMM 内容...]"
                  "\neg. $a 1/30 1630 melt x6, 1/31 2300 hrz")
async def a(ctx, *, events):
    events = re.split(", |,", events)  # split into list
    errored = True
    for event in events:
        if convert(event) == "invalid_date_format":
            embed = discord.Embed(description="Error: " + event + "\nInvalid date format (m/d)",
                                  colour=0xed6565)
            await ctx.send(embed=embed)
        elif convert(event) == "invalid_time_format":
            embed = discord.Embed(description="Error: " + event + "\nInvalid time format (HHMM)",
                                  colour=0xed6565)
            await ctx.send(embed=embed)
        elif convert(event)[0] == ValueError:
            embed = discord.Embed(description="Value Error: " + event + "\n" + str(convert(event)[1]),
                                  colour=0xed6565)
            await ctx.send(embed=embed)
        elif convert(event) == "dtPassed":
            embed = discord.Embed(description="Error: " + event + "\nReminder time has already passed",
                                  colour=0xed6565)
            await ctx.send(embed=embed)
        else:
            try:
                cur.execute("INSERT INTO user VALUES(?,?,?)",
                            (ctx.message.author.id, convert(event)[0], convert(event)[1]))
                con.commit()
                cur.execute("INSERT INTO reminders VALUES(?,?)", (convert(event)[0], ctx.message.author.id))
                con.commit()
                cur.execute("INSERT INTO archive VALUES(?,?,?)",
                            (ctx.message.author.id, convert(event)[0], convert(event)[1]))
                con.commit()
                errored = False
            except sqlite3.IntegrityError:
                embed = discord.Embed(description="Integrity Error: " + event + "\nan event is already exists at "
                                                                                "date-time",
                                      colour=0xed6565)
                await ctx.send(embed=embed)

    if not errored:
        res = cur.execute("SELECT * FROM user")
        print("add success\nuser table:")
        print(res.fetchall())
        res = cur.execute("SELECT * FROM reminders")
        print("reminders table:")
        print(res.fetchall())
        await ctx.send("Event(s) successfully added <:ln_hnm_fufufu:1011536521469366292>")


@bot.command(name="d",
             brief="刪除指定提醒事項",
             help="刪除指定提醒事項\n- events: 想刪除的事項的日期和時間"
                  "\n格式為 mm/dd HHMM[, mm/dd HHMM...]"
                  "\neg. $d 1/9 0900, 1/10 2330")
async def d(ctx, *, events):
    events = re.split(", |,", events)  # split into list
    errored = True
    for event in events:
        if convert(event)[0] == ValueError:
            embed = discord.Embed(description="Value Error: " + event + "\n" + str(convert(event)[1]),
                                  colour=0xed6565)
            await ctx.send(embed=embed)
        else:
            # check if reminder exists
            res = cur.execute("SELECT * FROM reminders WHERE dt = :dt AND uid = :uid",
                              {"dt": convert(event), "uid": ctx.message.author.id})
            if not res.fetchall():
                embed = discord.Embed(description="Error: " + event + "\nEvent does not exist",
                                      colour=0xed6565)
                await ctx.send(embed=embed)
            else:
                cur.execute("DELETE FROM user WHERE uid = :uid AND event_dt = :dt",
                            {"uid": ctx.message.author.id, "dt": convert(event)})
                con.commit()
                cur.execute("DELETE FROM reminders WHERE uid = :uid AND dt = :dt",
                            {"uid": ctx.message.author.id, "dt": convert(event)})
                con.commit()
                cur.execute("DELETE FROM archive WHERE uid = :uid AND event_dt = :dt",
                            {"uid": ctx.message.author.id, "dt": convert(event)})
                con.commit()
                errored = False

    if not errored:
        await ctx.send("Event(s) successfully deleted <:ln_hnm_fufufu:1011536521469366292>")


@bot.command(name="dall",
             brief="刪除所有提醒事項",
             help="刪除所有提醒事項")
async def dall(ctx):
    res = cur.execute("SELECT * FROM user WHERE uid = :uid", {"uid": ctx.message.author.id})
    if not res.fetchall():
        embed = discord.Embed(description="No reminders scheduled",
                              colour=0xed6565)
        await ctx.send(embed=embed)
        return

    cur.execute("DELETE FROM user WHERE uid = :uid",
                {"uid": ctx.message.author.id})
    con.commit()
    cur.execute("DELETE FROM reminders WHERE uid = :uid",
                {"uid": ctx.message.author.id})
    con.commit()
    cur.execute("DELETE FROM archive WHERE uid = :uid",
                {"uid": ctx.message.author.id})
    con.commit()

    await ctx.send("All events deleted <:ln_hnm_fufufu:1011536521469366292>")


@bot.command(name="me",
             brief="查看自己所有提醒事項",
             help="查看自己所有提醒事項")
async def me(ctx):
    events = cur.execute("SELECT event_dt, event_desc FROM user WHERE uid = :uid",
                         {"uid": ctx.message.author.id})
    events = events.fetchall()
    if not events:
        embed = discord.Embed(description="No reminders scheduled",
                              colour=0xed6565)
        await ctx.send(embed=embed)
        return

    me_list = []
    for dt in events:
        year = datetime.datetime.now().year
        month = dt[0][0:2]
        day = dt[0][2:4]
        hr = dt[0][4:6]
        min = dt[0][6:8]
        e_dt = datetime.datetime(int(year), int(month), int(day), int(hr), int(min), tzinfo=datetime.timezone.utc) + \
               datetime.timedelta(minutes=5)
        me_list.append([e_dt, dt[1]])
        me_list = sorted(me_list, key=lambda x: x[0])

    me_list = [[m[0].strftime("%m/%d %H%M"), m[1]] for m in me_list]
    message = ""
    for e in me_list:
        message = message + "\n" + e[0] + " :  " + e[1]
    await ctx.reply(message)


@bot.command(name='laf_r')
async def laf_r(ctx, skill: float):
    uid = str(ctx.message.author.id)
    user = cur.execute("SELECT * FROM bigFace WHERE uid = :uid",
                       {"uid": uid})
    user = user.fetchall()
    if not user:
        cur.execute("INSERT INTO bigFace(uid, skill) VALUES(?,?)",
                    (uid, skill))
        con.commit()
        await ctx.send("成功登記跑隊倍率 <:ln_hnm_fufufu:1011536521469366292>")
    else:
        cur.execute("UPDATE bigFace SET skill = ? WHERE uid = ?",
                    (skill, uid))
        con.commit()
        await ctx.send("成功更新跑隊倍率 <:ln_hnm_oh:1011638141364473866>")


@bot.command(name='laf')
async def laf(ctx, u1, u2, u3, u4, u5):
    users = []
    u1_skill = cur.execute("SELECT skill FROM bigFace WHERE uid = :uid",
                           {"uid": u1[2:-1]}).fetchone()
    print(u1_skill)
    if not u1_skill:
        await ctx.send("有人沒用`$laf_r`登記跑隊倍率 <:ln_hnm_sorry:1015609265035161650>")
        return
    else:
        users.append([u1, u1_skill])
    u2_skill = cur.execute("SELECT skill FROM bigFace WHERE uid = :uid",
                           {"uid": u2[2:-1]}).fetchone()
    if not u2_skill:
        await ctx.send("有人沒用`$laf_r`登記跑隊倍率 <:ln_hnm_sorry:1015609265035161650>")
        return
    else:
        users.append([u2, u2_skill])
    u3_skill = cur.execute("SELECT skill FROM bigFace WHERE uid = :uid",
                           {"uid": u3[2:-1]}).fetchone()
    if not u3_skill:
        await ctx.send("有人沒用`$laf_r`登記跑隊倍率 <:ln_hnm_sorry:1015609265035161650>")
        return
    else:
        users.append([u3, u3_skill])
    u4_skill = cur.execute("SELECT skill FROM bigFace WHERE uid = :uid",
                           {"uid": u4[2:-1]}).fetchone()
    if not u4_skill:
        await ctx.send("有人沒用`$laf_r`登記跑隊倍率 <:ln_hnm_sorry:1015609265035161650>")
        return
    else:
        users.append([u4, u4_skill])
    u5_skill = cur.execute("SELECT skill FROM bigFace WHERE uid = :uid",
                           {"uid": u5[2:-1]}).fetchone()
    if not u5_skill:
        await ctx.send("有人沒用`$laf_r`登記跑隊倍率 <:ln_hnm_sorry:1015609265035161650>")
        return
    else:
        users.append([u5, u5_skill])
    print(users)

    users.sort(key=lambda x: x[1], reverse=True)
    uids = [u[0] for u in users]
    order = ['', '', '', '', '']
    order[0] = uids[4]
    order[1] = uids[1]
    order[2] = uids[0]
    order[3] = uids[2]
    order[4] = uids[3]
    message = "**大臉站位** <:ln_hnm_smile:1024341146878611496>\n"
    for mention in order:
        message = message + " " + mention
    await ctx.send(message)


@bot.command(name='shrimp_r')
async def shrimp_r(ctx, skill: float):
    uid = str(ctx.message.author.id)
    user = cur.execute("SELECT * FROM shrimpSkill WHERE uid = :uid",
                       {"uid": uid})
    user = user.fetchall()
    if not user:
        cur.execute("INSERT INTO shrimpSkill(uid, skill) VALUES(?,?)",
                    (uid, skill))
        con.commit()
        await ctx.send("成功登記拍蝦隊伍倍率 <:ln_hnm_fufufu:1011536521469366292>")
    else:
        cur.execute("UPDATE shrimpSkill SET skill = ? WHERE uid = ?",
                    (skill, uid))
        con.commit()
        await ctx.send("成功更新拍蝦隊伍倍率 <:ln_hnm_oh:1011638141364473866>")


@bot.command(name='shrimp')
async def shrimp(ctx, u1, u2, u3, u4, u5):
    users = []
    u1_skill = cur.execute("SELECT skill FROM shrimpSkill WHERE uid = :uid",
                           {"uid": u1[2:-1]}).fetchone()
    print(u1_skill)
    if not u1_skill:
        await ctx.send("有人沒用`$shrimp_r`登記拍蝦隊伍倍率 <:ln_hnm_sorry:1015609265035161650>")
        return
    else:
        users.append([u1, u1_skill])
    u2_skill = cur.execute("SELECT skill FROM shrimpSkill WHERE uid = :uid",
                           {"uid": u2[2:-1]}).fetchone()
    if not u2_skill:
        await ctx.send("有人沒用`$shrimp_r`登記拍蝦隊伍倍率 <:ln_hnm_sorry:1015609265035161650>")
        return
    else:
        users.append([u2, u2_skill])
    u3_skill = cur.execute("SELECT skill FROM shrimpSkill WHERE uid = :uid",
                           {"uid": u3[2:-1]}).fetchone()
    if not u3_skill:
        await ctx.send("有人沒用`$shrimp_r`登記拍蝦隊伍倍率 <:ln_hnm_sorry:1015609265035161650>")
        return
    else:
        users.append([u3, u3_skill])
    u4_skill = cur.execute("SELECT skill FROM shrimpSkill WHERE uid = :uid",
                           {"uid": u4[2:-1]}).fetchone()
    if not u4_skill:
        await ctx.send("有人沒用`$shrimp_r`登記拍蝦隊伍倍率 <:ln_hnm_sorry:1015609265035161650>")
        return
    else:
        users.append([u4, u4_skill])
    u5_skill = cur.execute("SELECT skill FROM shrimpSkill WHERE uid = :uid",
                           {"uid": u5[2:-1]}).fetchone()
    if not u5_skill:
        await ctx.send("有人沒用`$shrimp_r`登記拍蝦隊伍倍率 <:ln_hnm_sorry:1015609265035161650>")
        return
    else:
        users.append([u5, u5_skill])

    users.sort(key=lambda x: x[1], reverse=True)
    uids = [u[0] for u in users]
    order = ['', '', '', '', '']
    order[0] = uids[2]
    order[1] = uids[3]
    order[2] = uids[4]
    order[3] = uids[1]
    order[4] = uids[0]
    message = "**蝦車站位** <:ln_hnm_smile:1024341146878611496>\n"
    for mention in order:
        message = message + " " + mention
    await ctx.send(message)


@bot.command(name="honami",
             brief="指令介紹",
             help="穗波的指令介紹")
async def honami(ctx):
    embed = discord.Embed(title="__穗波指令表__",
                          description="望月穗波bot由SK所寫，提供提醒用的功能，穗波會在你的提醒事項前5分鐘在 <#1029506502312087582> "
                                      "@你\n\n按 \"你的提醒事項\" 可以顯示穗波正在提醒你的事項，提醒完該提醒事項會被自動刪除\n\n"
                                      "同時可以領取提醒身份組，穗波會每天在指定的時間提醒你"
                                      "\n\n**$a <events>**\n新加提醒事項"
                                      "\nevents: mm/dd HHMM 内容[, mm/dd HHMM 内容...]"
                                      "\n例: $a 1/30 0715 melt x5"
                                      "\n例: $a 1/30 1630 melt x6, 1/31 2300 hrz"
                                      "\n\n**$d <events>**\n刪除指定提醒事項"
                                      "\nevents: mm/dd HHMM[, mm/dd HHMM...]"
                                      "\n例: $d 1/30 1630, 1/31 2300"
                                      "\n\n**$dall**\n刪除所有提醒事項"
                                      "\n\n**$me**\n查看自己所有提醒事項"
                                      "\n\n**$r <url>**\n用發車信息的鏈接查看該消體車的報班紀錄等資訊"
                                      "\n\n**$refillstart**\n開始每兩分鐘一次的回體提醒"
                                      "\n\n**$refillstop**\n停止每兩分鐘一次的回體提醒"
                                      "\n\n**$honami**\n顯示此指令介紹，指令表會定期更新\n** **",
                          colour=0xed6565)
    embed.set_footer(text="最後更新: 3/5/2024")
    await ctx.send(embed=embed)


@bot.command(name="create", hidden=True)
async def create(ctx):
    user = """ CREATE TABLE user (
            uid VARCHAR(25),
            event_dt VARCHAR(30),
            event_desc VARCHAR(255) NOT NULL,
            PRIMARY KEY(uid, event_dt)
        ); """
    reminders = """ CREATE TABLE reminders (
            dt VARCHAR(30),
            uid VARCHAR(25),
            PRIMARY KEY(dt, uid)
        ); """
    cur.execute(user)
    cur.execute(reminders)
    cur.execute("CREATE TABLE archive AS SELECT * FROM user")
    melt = """ CREATE TABLE melt (
            mid VARCHAR(30) PRIMARY KEY,
            dt VARCHAR(30) NOT NULL, 
            driver VARCHAR(30) NOT NULL,
            cno INTEGER NOT NULL,
            record TEXT
            ); """
    meltUsers = """ CREATE TABLE meltUsers (
            mid VARCHAR(30),
            uid VARCHAR(30),
            PRIMARY KEY(mid, uid)
        ); """
    shrimp = """ CREATE TABLE shrimp (
                mid VARCHAR(30) PRIMARY KEY,
                dt VARCHAR(30) NOT NULL, 
                driver VARCHAR(30) NOT NULL,
                cno INTEGER NOT NULL,
                record TEXT
                ); """
    shrimpUsers = """ CREATE TABLE shrimpUsers (
                mid VARCHAR(30),
                uid VARCHAR(30),
                PRIMARY KEY(mid, uid)
            ); """
    bigFace = """ CREATE TABLE bigFace (
                    uid VARCHAR(30),
                    skill REAL,
                    PRIMARY KEY(uid)
                ); """
    shrimpSkill = """ CREATE TABLE shrimpSkill (
                    uid VARCHAR(30),
                    skill REAL,
                    PRIMARY KEY(uid)
                ); """
    cur.execute(melt)
    cur.execute(meltUsers)
    cur.execute(shrimp)
    cur.execute(shrimpUsers)
    cur.execute(bigFace)
    cur.execute(shrimpSkill)


@bot.command(name="q", hidden=True)
async def q(ctx, *, sql):
    if ctx.message.author.id != 598066719659130900:
        return
    res = cur.execute(sql)
    res = res.fetchall()
    try:
        print(res)
        await ctx.send(res)
    except Exception as e:
        print(e)


@bot.command(name='clear', hidden=True)
async def clear(ctx, tablename):
    sql = "DELETE FROM " + tablename
    cur.execute(sql)
    con.commit()


@bot.command(name="refillstart",
             brief="開始回體提醒",
             help="開始每兩分鐘一次的回體提醒")
async def refillstart(ctx):
    global refill_ids
    mention = "<@" + str(ctx.author.id) + ">"
    refill_ids.append(mention)
    await ctx.send("<:z_livebonus:1006937417900642426> refill reminder initiated")


@bot.command(name="refillstop",
             brief="停止回體提醒",
             help="停止每兩分鐘一次的回體提醒")
async def refillstop(ctx):
    global refill_ids
    mention = "<@" + str(ctx.author.id) + ">"
    refill_ids.remove(mention)
    await ctx.send("<:z_livebonus:1006937417900642426> refill reminder stopped")


@bot.command(name="refillcheck", hidden=True)
async def refillcheck(ctx):
    global refill_ids
    await ctx.send(refill_ids)


# --------- test tiuzeen reminder ---------

@bot.command(name="test", hidden=True)
async def test(ctx):
    bot.reminder_ids = []
    guild = bot.get_guild(1006236899570110614)
    role = guild.get_role(1029704053665570836)

    for user in guild.members:
        if role in user.roles:
            bot.reminder_ids.append(user.id)
    print(bot.reminder_ids)
    test_msg = await ctx.send("reminder test")
    bot.reminder_msg_id = test_msg.id
    reaction = bot.get_emoji(1082662447569186816)
    await test_msg.add_reaction(reaction)


@bot.command(name='test2', hidden=True)
async def test2(ctx):
    channel = bot.get_channel(1007203228515057687)
    test_msg = await channel.fetch_message(bot.reminder_msg_id)
    for r in test_msg.reactions:
        async for user in r.users():
            if user.id in bot.reminder_ids:
                bot.reminder_ids.remove(user.id)

    await ctx.send(bot.reminder_ids)


@bot.command(name="checkloop", hidden=True)
async def checkloop(ctx):
    if reminder.is_running():
        await ctx.send("loop running")
    else:
        await ctx.send("loop not running, attempting to start...")
        reminder.start()
        if reminder.is_running():
            await ctx.send("loop running")
        else:
            await ctx.send("loop failed to start")


@bot.command(name="get_reminder_ids", hidden=True)
async def get_reminder_ids(ctx):
    bot.reminder_ids = []
    guild = bot.get_guild(1006236899570110614)
    role = guild.get_role(1029704053665570836)
    for user in guild.members:
        if role in user.roles:
            bot.reminder_ids.append(user.id)
    await ctx.send(str(bot.reminder_ids) + "\n換日 reminder ids added.")


@reminder.error
async def reminder_exited(self):
    print(self)
    channel = bot.get_channel(1007203228515057687)
    await channel.send("reminder loop errored <@598066719659130900>, error:")
    await channel.send(self)
    reminder.restart()
    await channel.send("reminder restarted")


bot.run(TOKEN)
