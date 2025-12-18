import os

import pytest
from rich.style import Style

from logrich import log
from logrich.app import console

obj = {
    "name": "Имя, фамилия " * 5,
    "slug": 759933327936,
    "slug1": 13,
    "slug2": 51,
    "slug-test": 198,
    "slug3": 951,
    "href": "http://0.0.0.0:8000/downloads/pf-pf4-2050596-e4b8eff7.xlsx",
    "digest": "e4b8eff72593c54e40a3f0dfa3aff156",
    "message": "File pf-pf4-2050596-e4b8eff7 created now",
    "score": 123456,
    "elapsed_time": "0.060 seconds",
    "version": "2.14.3",
    "access": "eyJ0AiiJKV1QiLCJhbGcizI1NiJ912.eyJ0btlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjUzNTUwMTY1LCJqdGkiOiJmNzFhYjg5OWE5MDY0Y2EwODgwMzY1NzQ1NjYwNzdjOSIsInVzZXJfaWQiOjF9.KES3fhmBTXy8AwDSJTseNsLFC3xSh1J_slndgmSwp08",
    "id": 1234561,
}


# @rich.repr.auto
# декоратор формирует __repr_rich__ на основе __init__ объекта
class Bird:
    def __init__(self, name, eats=None, fly=True, extinct=False):
        self.name = name
        self.eats = list(eats) if eats else []
        self.fly = fly
        self.extinct = extinct

    def __repr__(self):
        return f"Bird({self.name}, eats={self.eats!r}, fly={self.fly!r}, extinct={self.extinct!r})"


BIRDS = {
    "gull": Bird("gull", eats=["fish", "chips", "ice cream", "sausage rolls"]),
    "penguin": Bird("penguin", eats=["fish"], fly=False),
    "dodo": Bird("dodo", eats=["fruit"], fly=False, extinct=True),
}

temp_reason = "\033[38;5;196mВременно отключен, должен быть включен."

# skip = False
skip = True
skip_item = False
# skip_item = True
skipmark = pytest.mark.skipif(skip, reason=temp_reason)
skipmark_item = pytest.mark.skipif(skip_item, reason=temp_reason)


# @skipmark
def test_one():
    log.trace("Сообщение уровня TRACE: 5")
    log.debug("Сообщение уровня DEBUG: 10")
    log.info("Сообщение уровня INFO: 20")
    log.success("Сообщение уровня SUCCESS: 25")
    log.warning("Сообщение уровня WARNING: 30")
    log.error("Сообщение уровня ERROR: 40; " * 10)
    log.fatal("Это катастрофа, парень шел к успеху, но не фартануло..:-(\nСообщение уровня CRITICAL: 50")
    log.debug(BIRDS, title="Объект птички")
    log.info(obj, title="Словарь")
    # return
    log.success("SUCCESS [#FF1493]SUCCESS[/] [#00FFFF]SUCCESS[/] " * 10)
    log.debug("=" * 70)

    title = "Это Спарта!!"
    console.rule(f"[green]{title}[/]", style=Style(color="magenta"))

    num_dict = {
        1: {2: {2: 111}, 3: {3: 111}},
        2: {3: {3: 111}},
        3: {2: {2: 111}, 3: {3: 111}},
    }
    log.debug(num_dict, title="неверно раскрашивает первые числа")
    num_dict = {
        1: {2: {2: "здесь будут стили"}, 3: {3: "здесь будут стили"}},
        2: {3: {3: "здесь будут стили"}},
        3: {2: {2: "здесь будут стили"}, 3: {3: "здесь будут стили"}},
    }
    log.debug(num_dict, title="неверно раскрашивает первые двойки")

    context = {"clientip": "192.168.0.1", "user": "fbloggs1"}  # noqa F841

    # logger.info("Protocol problem", extra=context)  # Standard logging
    # logger.bind(**context).info("Protocol problem")  # Loguru


# @skipmark
def test_too():
    # TEST = log.level("TEST")
    # TST = "<red>TST"
    # TST = "TST"
    # TST = "[reverse gray70] TST      [/]"
    # TST = "[reverse yellow] TST      [/]"
    # log.level(TST, no=15)
    # log.level(TST, no=15, style="red")
    # log.log(TST, "Тестовый лог")
    # log.tst = lambda msg: log.log(TST, msg)
    log.test("Тестовый лог")
    log.start("Тестовый лог")
    log.pprint("Тестовый лог PPRINT")
    log.debug((1, 2))
    log.trace(os.get_terminal_size())
    # assert None, "--"
    log.debug(3, 4)
    log.trace()
    log.success("foo", "bar")
    log.trace(*["baz2", "bar"])
    log.success("foo", "bar", title="Заголовок сообщения")
    log.info("foo bar", title="Заголовок сообщения")
    log.debug("*8" * 10)

    log.api("api " * 10)
    log.app("app " * 10)
    log.arg("arg " * 10)
    log.arr("arr " * 10)
    log.bin("bin " * 10)
    log.bit("bit " * 10)
    log.bug("bug " * 10)
    log.bus("bus " * 10)
    log.cpu("cpu " * 10)
    log.dns("dns " * 10)
    log.doc("doc " * 10)
    log.env("env " * 10)
    log.err("err " * 10)
    log.hex("hex " * 10)
    log.ide("ide " * 10)
    log.key("key " * 10)
    log.lib("lib " * 10)
    log.map("map " * 10)
    log.max("max " * 10)
    log.min("min " * 10)
    log.net("net " * 10)
    log.npm("npm " * 10)
    log.obj("obj " * 10)
    log.opt("opt " * 10)
    log.pop("pop " * 10)
    log.ram("ram " * 10)
    log.raw("raw " * 10)
    log.ref("ref " * 10)
    log.reg("reg " * 10)
    log.res("res " * 10)
    log.row("row " * 10)
    log.set("set " * 10)
    log.sql("sql " * 10)
    log.sum("sum " * 10)
    log.tcp("tcp " * 10)
    log.tmp("tmp " * 10)
    log.txt("txt " * 10)
    log.url("url " * 10)
    log.usr("usr " * 10)
    log.var("var " * 10)
    log.web("web " * 10)
    log.zip("zip " * 10)
    log.abs("abs " * 10)
    log.ace("ace " * 10)
    log.act("act " * 10)
    log.add("add " * 10)
    log.age("age " * 10)
    log.aid("aid " * 10)
    log.air("air " * 10)
    log.all("all " * 10)
    log.and_("and " * 10)
    log.any("any " * 10)
    log.arc("arc " * 10)
    log.arm("arm " * 10)
    log.art("art " * 10)
    log.ask("ask " * 10)
    log.bad("bad " * 10)
    log.bag("bag " * 10)
    log.ban("ban " * 10)
    log.bar("bar " * 10)
    log.bat("bat " * 10)
    log.bed("bed " * 10)
    log.bee("bee " * 10)
    log.big("big " * 10)
    log.box("box " * 10)
    log.boy("boy " * 10)
    log.bud("bud " * 10)
    log.but("but " * 10)
    log.bye("bye " * 10)
    log.cab("cab " * 10)
    log.cap("cap " * 10)
    log.car("car " * 10)
    log.cat("cat " * 10)
    log.cup("cup " * 10)
    log.day("day " * 10)
    log.did("did " * 10)
    log.die("die " * 10)
    log.dig("dig " * 10)
    log.dim("dim " * 10)
    log.dog("dog " * 10)
    log.dot("dot " * 10)
    log.dry("dry " * 10)
    log.ear("ear " * 10)
    log.eat("eat " * 10)
    log.egg("egg " * 10)
    log.era("era " * 10)
    log.eve("eve " * 10)
    log.fab("fab " * 10)
    log.fan("fan " * 10)
    log.far("far " * 10)
    log.fat("fat " * 10)
    log.fax("fax " * 10)
    log.fee("fee " * 10)
    log.fig("fig " * 10)
    log.fin("fin " * 10)
    log.fit("fit " * 10)
    log.fix("fix " * 10)
    log.fly("fly " * 10)
    log.fog("fog " * 10)
    log.fox("fox " * 10)
    log.fun("fun " * 10)
    log.gap("gap " * 10)
    log.gas("gas " * 10)
    log.gem("gem " * 10)
    log.get("get " * 10)
    log.gun("gun " * 10)
    log.guy("guy " * 10)
    log.had("had " * 10)
    log.has("has " * 10)
    log.hat("hat " * 10)
    log.him("him " * 10)
    log.hit("hit " * 10)
    log.hop("hop " * 10)
    log.hot("hot " * 10)
    log.ice("ice " * 10)
    log.ink("ink " * 10)
    log.its("its " * 10)
    log.jam("jam " * 10)
    log.jaw("jaw " * 10)
    log.jet("jet " * 10)
    log.job("job " * 10)
    log.joy("joy " * 10)
    log.kid("kid " * 10)
    log.kit("kit " * 10)
    log.lab("lab " * 10)
    log.lap("lap " * 10)
    log.law("law " * 10)
    log.led("led " * 10)
    log.let("let " * 10)
    log.lot("lot " * 10)
    log.man("man " * 10)
    log.may("may " * 10)
    log.men("men " * 10)
    log.mix("mix " * 10)
    log.mob("mob " * 10)
    log.mod("mod " * 10)
    log.now("now " * 10)
    log.odd("odd " * 10)
    log.off("off " * 10)
    log.old("old " * 10)
    log.one("one " * 10)
    log.our("our " * 10)
    log.out("out " * 10)
    log.own("own " * 10)
    log.pad("pad " * 10)
    log.pan("pan " * 10)
    log.pay("pay " * 10)
    log.pod("pod " * 10)
    log.pro("pro " * 10)
    log.pub("pub " * 10)
    log.rag("rag " * 10)
    log.ray("ray " * 10)
    log.rub("rub " * 10)
    log.sad("sad " * 10)
    log.say("say " * 10)
    log.sea("sea " * 10)
    log.see("see " * 10)
    log.six("six " * 10)
    log.sky("sky " * 10)
    log.spy("spy " * 10)
    log.sub("sub " * 10)
    log.sun("sun " * 10)
    log.tab("tab " * 10)
    log.tag("tag " * 10)
    log.tip("tip " * 10)
    log.too("too " * 10)
    log.top("top " * 10)
    # log.use("use " * 10)
    log.was("was+" * 10)
    log.way("way=" * 10)
    log.win("win-" * 10)
    log.lib("lib " * 10)
    log.mix("mix " * 10)
    log.win(set(["win", "set"]))
