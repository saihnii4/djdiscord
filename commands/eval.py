import ast
import time
import dataclasses
import typing
import discord
import rethinkdb

import discord.ext.commands


def insert_returns(body: list):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)

@dataclasses.dataclass
class Evaluation:
    author: typing.Union[discord.Member, discord.User, int]
    error: typing.Optional[Exception] = None
    result: typing.Optional[str] = None
    execution_time: typing.Optional[int] = None
    message: typing.Optional[discord.Message] = None

    async def destruct(self):
        await self.message.delete(delay=10)

class EvaluationParser(discord.ext.commands.Converter):
    async def convert(self, ctx: discord.ext.commands.Context, argument: str) -> Evaluation:
        code = "\n".join(f"    {i}" for i in argument.strip("` py`").splitlines())
        
        print(code)

        body = "async def _evaluation():\n{}".format(code)

        syntax = ast.parse(body)

        parsed_body = syntax.body[0].body

        insert_returns(parsed_body)

        env = {
            "ctx": ctx,
            "discord": discord,
            "commands": discord.ext.commands,
            "bot": ctx.bot,
            "r": rethinkdb.r,
            "__import__": __import__
        }

        exec(compile(syntax, filename="<ast>", mode="exec"), env)

        result = Evaluation(ctx.author)

        try:
            start = time.time()
            execution_output = (await eval("_evaluation()", env))
            result.execution_time = round(time.time() - start, 15)
            result.result = execution_output
        except Exception as error:
            result.error = error
        
        return result

@discord.ext.commands.command(name="eval")
@discord.ext.commands.is_owner()
async def evaluate(ctx: discord.ext.commands.Context, *, evaluation: EvaluationParser) -> None:
    payload = ctx.bot.templates.eval.copy()

    payload.add_field(name="Result", value="```{0.result}```".format(evaluation))
    payload.add_field(name="Error", value="```{0.error}```".format(evaluation))
    payload.add_field(name="Executor", value="```{0.author}```".format(evaluation))
    payload.add_field(name="Execution Time", value="```{0.execution_time} seconds```".format(evaluation), inline=False)

    message = await ctx.send(embed=payload)
    evaluation.message = message
    await evaluation.destruct()

def setup(bot: discord.ext.commands.Bot) -> None:
    bot.add_command(evaluate)
