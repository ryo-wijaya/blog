---
layout: post
title: "Why Stock Options are Beautiful"
description: >-
  The fundamentals of stock options and why they can be an extremely useful tool in your arsenal.
author: ryo
date: 2026-03-09 23:43:02 +0800
categories: [Finance]
tags: [finance, stocks, derivatives, markets, options]
image:
  path: assets/img/others/theta-gang.jpg
  alt: Thetagang!
toc: true
comments: true
pin: false
published: true
---

## Overview

Deep-dive into options based on [Equities and Derivatives Fundamentals](/posts/finance/equities-and-derivatives-fundamentals/).

Among the people I talk to, stock options can sometimes have a bad name. Many people recall reading about option trading horror stories, and assume that dealing with options is an easy way to be rewarded with infinite liability due to excessive leverage and elevated risks. In my opinion, options are a double-edged sword. Due to their complexity, how you may benefit or be ruined from options depends entirely on how you use them. In some cases, they can even be less risky than buying stocks outright (see [the wheel strategy](#the-wheel)).

---

## What are Stock Options?

A stock option is a contract that gives you the right, but not the obligation, to buy or sell shares of a stock at a specific price (the strike price) before or on a specific date (the expiration date). One contract almost always represents 100 shares.

There are two types:
- **Call** - the right to buy at the strike price. You want the stock to go up.
- **Put** - the right to sell at the strike price. You want the stock to go down.

You can either buy or sell options. When buying, the price you pay for this contract is called the **premium**, which goes to the seller. The buyer's max loss is always just the premium paid. The seller collects that premium upfront but takes on the obligation to fulfill the contract if the buyer exercises.

Compared to stocks, options add three layers of complexity: time decay, leverage, and volatility sensitivity.

### Contract Terms

- **Strike price** - the price at which you have the right to buy (call) or sell (put)
- **Expiration date** - when the contract expires. Could be days, weeks, months, or years (LEAPS) out
- **Premium** - what you pay as a buyer or collect as a seller
- **ITM / ATM / OTM** - a call is In-the-money (ITM) if the stock is above the strike, Out-of-the-money (OTM) if below. At-the-money (ATM) means it's right at the strike. As a buyer you are happy when the contract is ITM, and unhappy when it's OTM. As a seller it's the opposite.

### An Example with Call Options

The current price of NASDAQ: NVDA (Nvidia) is $180.
- **Alice's Bet**: Alice thinks Nvidia will not rise above $170 in 1 month's time. She sells a **call** with a **strike of $170**, expiring in 1 month.
- **Bob's Bet**: Bob disagrees, he thinks Nvidia will hit $190 at least. He buys the contract from Alice for **$15 per share** (the market price), so $15 x 100 = **$1,500** leaves Bob's account and goes to Alice's immediately at the time of purchase (ignoring market makers exist).

**This essentially means that Alice has promised to sell Bob 100 Nvidia shares at $170 if the price is above $170 at expiration. If it stays below, Bob has no reason to exercise and the contract expires worthless.**

Assuming neither closes their position early:

| Scenario | Alice | Bob |
|---|---|---|
| Nvidia drops to $169 | +$1,500 (keeps full premium) | -$1,500 (contract expires worthless) |
| Nvidia rises to $180 | -$1,000 on shares + $1,500 premium = **+$500** | +$1,000 on shares - $1,500 paid = **-$500** |
| Nvidia rises to $185 | -$1,500 on shares + $1,500 premium = **$0** | +$1,500 on shares - $1,500 paid = **$0** |
| Nvidia rises to $190 | -$2,000 on shares + $1,500 premium = **-$500** | +$2,000 on shares - $1,500 paid = **+$500** |

As seen above, buying a call has a fixed max loss (the premium). Selling a naked call has theoretically unlimited loss. If Nvidia dropped to $0, Bob loses only his $1,500 paid for the contract. But if Nvidia rose to $1,000, Alice would have to buy 100 shares at $1,000 to sell them to Bob at $170, a loss of $81,500.

### Why not just buy the Shares?

Options let you control 100 shares for a fraction of the cost. This is called **leverage**. If a stock is at $200, buying 100 shares costs $20,000. A call option on the same stock might cost $300. If the stock runs up $20, your shares gain $2,000 (10%). Your option could gain several times that percentage-wise because of leverage.

The flip side is that options expire. Shares don't. If you buy shares and the stock goes sideways for 6 months, you can just wait. With options, the contract loses value every single day that passes even if the price doesn't move. That's time decay (theta).

So why use them? Because there are many ways to use them depending on your goal, some conservative and some extremely risky. Most brokers classify options strategies into 3-5 risk levels, and you may need approval to access the higher ones.

### The Math Behind Option Prices

The premium has two components:

**Intrinsic value** - how much the option is worth right now if exercised immediately. Only ITM options have intrinsic value. A $170 strike call on a $180 stock has $10 of intrinsic value. OTM options have zero.

**Extrinsic value (time value)** - everything else. This value represents the market's expectation that the stock could still move favorably before expiration. This decays to zero by expiration day regardless of what the stock does. This is what sellers are collecting.

Following the Nvidia example, Alice sold Bob a call option contract for a strike of $170 when the current price was $180, expiring in 1 month's time. This contract cost Bob $1,500. This $1,500 is made up of $1,000 of intrinsic value ($10 per share). The other $500 is extrinsic value, and is affected by the Greeks (mathematical factors).  

The Greeks that drive the price:

- **Delta** - how much the option price moves per $1 move in the stock. A 0.5 delta call gains ~$0.50 per $1 the stock goes up. Also approximates the probability the option expires ITM. It can also indicate how many shares of a stock an option acts like. A delta of 0.40 means one option contract behaves similarly to owning (for calls) or shorting (for puts) 40 shares of the underlying stock.
- **Theta** - how much value the option loses per day from time decay. Always negative for buyers, always positive for sellers. Accelerates very quickly as expiration approaches, especially around the 1 month to expiry mark.
- **Vega** - sensitivity to implied volatility (IV). Higher IV means more expensive options. If you buy before earnings when IV is elevated and the stock moves as expected but IV collapses after, you can still lose money. This is called an IV crush.
- **Gamma** - rate of change of delta. High gamma means delta shifts fast, which matters a lot near expiration.

Skip here for a [deep-dive into the Greeks](/posts/finance/a-deep-dive-into-the-greeks/).

---

## Stock Option Strategies

Options can be used in a few different ways depending on what you're trying to do.

### Leveraged Play

Buying calls or puts outright to take a directional bet with leverage. You put up less capital than buying shares, but you can lose 100% of what you paid if the trade goes wrong.

**Example: 3-month call on NVDA**

Nvidia is at $180. You think it will run up significantly over the next quarter. Buying 100 shares outright costs $18,000. Instead, you buy 1 call contract with a **$185 strike expiring in 3 months**, paying a premium of **$12 per share = $1,200**.

| Scenario | Shares ($18,000) | Call Option ($1,200) |
|---|---|---|
| NVDA drops to $160 | -$2,000 (-11%) | -$1,200 (-100%) |
| NVDA stays at $180 | $0 (0%) | ~-$600 (-50%, theta decay) |
| NVDA rises to $200 | +$2,000 (+11%) | ~+$1,800 (+150%) |
| NVDA rises to $220 | +$4,000 (+22%) | ~+$4,800 (+300%) |

The option gives you massive upside leverage for a fraction of the capital. But if Nvidia goes sideways or drifts slightly down, you lose most or all of the $1,200, whereas the shareholder barely feels it. Time is the enemy here.

**Example: 2-year LEAPS call on NVDA**

LEAPS (Long-term Equity Anticipation Securities) are options with expiration dates 1-2 years out. Because they have so much time, they cost more, but theta decay is slow in the early months. They are often used as a cheaper long-term substitute for owning shares.

Nvidia is at $180. You buy 1 call contract with a **$150 strike expiring in 2 years (deep ITM)**, paying a premium of **$55 per share = $5,500**. At this strike, the intrinsic value alone is $30 per share ($3,000), and you're paying the remaining $2,500 for the time value.

| Scenario (at expiry) | Shares ($18,000) | LEAPS ($5,500) |
|---|---|---|
| NVDA drops to $100 | -$8,000 (-44%) | -$5,500 (-100%) |
| NVDA stays at $180 | $0 (0%) | +$3,000 (+55%, intrinsic only) |
| NVDA rises to $250 | +$7,000 (+39%) | +$9,500 (+173%) |
| NVDA rises to $350 | +$17,000 (+94%) | +$19,500 (+355%) |

Deep ITM LEAPS behave similarly to owning shares (high delta, ~0.80+) but at a much lower cost basis. The trade-off is that if the stock crashes hard enough to go below your strike, the entire premium is gone. LEAPS are also commonly used as the long leg in a [PMCC](#pmcc-poor-mans-covered-call).

### Gambling

Buying short-dated OTM options for a directional bet. This is the most common way people blow up their accounts with options, and is also the reason most people tell you to avoid messing with options. 

**0DTEs and 1DTEs** (zero or one day to expiration) are extremely high gamma, meaning small moves in the stock create massive swings in the option price. A 5% move on the stock can mean a 200% gain or a total loss on the option. Theta is at maximum here, so the option is losing value every minute it's not moving in your favor (which makes sense as it is literally about to expire).

These are attractive because they are cheap to buy. Because people usually go for OTM ones, there is almost no intrinsic value, all of the value is extrinsic, which makes it susceptible to huge moves. For example, a single OTM contract for Nvidia expiring in 30 minutes can cost $0.05 ($5 total), and a small move in the stock price toward your strike can increase its value to $0.10, doubling your money instantly. The downside? You will lose everything in 30 minutes if the stock does not move your way. It's pure gambling.

### Hedging

In its simplest example, this is buying puts to protect a position you don't want to sell. If you hold 500 shares of a stock and want protection against a drawdown, you can buy put options.

You hold 500 shares of Nvidia at $180, worth $90,000. Earnings are coming up and you don't want to sell, but you're worried about a drop. You buy 5 put contracts (500 shares) with a **$170 strike expiring in 1 month**, paying a premium of **$5 per share = $2,500 total**.

| Scenario | Portfolio (500 shares) | With Put Hedge | Net |
|---|---|---|---|
| NVDA stays at $180 | $0 | -$2,500 (expired worthless) | **-$2,500** |
| NVDA drops to $170 | -$5,000 | -$2,500 (expired worthless) | **-$7,500** |
| NVDA drops to $160 | -$10,000 | +$5,000 on puts - $2,500 paid = **+$2,500** | **-$7,500** |
| NVDA drops to $140 | -$20,000 | +$15,000 on puts - $2,500 paid = **+$12,500** | **-$7,500** |

Once the stock falls below $170, your puts kick in and offset the losses dollar-for-dollar. Your maximum loss is capped at $7,500 regardless of how far the stock falls. Think of the $2,500 premium as the cost of insurance.

Portfolio managers use this at scale with index puts (SPX, SPY). For retail, it's most relevant around earnings if you're long on a volatile stock and don't want to sell your position. Note that around earnings seasons it might be pretty expensive to buy puts due to increased IV (vega).

### Income Generation

These usually bank on selling options to collect premium repeatedly, not buying. Buying puts you at the mercy of time and volatility, selling does not. This is mostly what I like to do and I think it's genuinely useful for retail investors.

**Covered Calls (CCs)** - you own 100 shares and sell a call above the current price. You collect the premium. If the stock stays below the strike at expiration, the contract expires worthless and you keep the premium. If it goes above, your shares get called away at the strike. Usually you do this if you think the price is unlikely to rise in the short-term. The downside is that if your stock rallies 1000%, you will be forced to sell at the strike. You cap your upside but get paid for it. You can do this weekly, bi-weekly or even monthly for steady income, provided your shares do not get called away. 

*For example, Nvidia is $180. You sell a call at $185 strike expiring in a week for $300. If Nvidia goes above $185 in a week, you are forced to let go of your 100 shares for $185 per unit, if not, the contract expires and you keep your shares. Either way, you keep the $300 free-of-charge 🙂, not bad.*

**Cash-Secured Puts (CSPs)** - you sell a put at a price you'd be happy buying the stock at. You collect premium. If the stock stays above the strike, it expires worthless and you keep the premium. If it drops below, you get assigned 100 shares at the strike (but net cost is reduced by the premium collected). 

*For example, Nvidia is $180. You think the price is good, but can be even better. You sell a put at strike $175 for $300, making sure you have the money in your account to buy 100 units should the price actually drops to $175. If Nvidia drops to $170 in a week, you are forced to buy it at $175. Considering that you were willing to pay $180 for the stock anyways, $175 is not a bad deal. If Nvidia stays above $175, the contract expires and you are released from your obligation. Either way, you keep the $300 free-of-charge as well.*

<span id="the-wheel"></span>
**The Wheel** - combining both CCs and CSPs. Sell cash-secured puts until you get assigned shares. Then sell covered calls on those shares until they get called away. Repeat. In a sideways or slowly rising market, this generates consistent income. The real risk is if the stock drops significantly while you're holding the shares. If you follow the rule of only selling CSPs on stocks you are fine with owning at the strike, this is a **less risky way of playing in the stock market**, as your premium cushions your cash outflows, and you might not even get assigned your shares (or you might get shares called away right before they dump). This strategy overall will cap your upside, making it one of the most risk-averse ways of investing in my opinion.

<span id="pmcc-poor-mans-covered-call"></span>
**PMCC (Poor Man's Covered Call)** - instead of owning 100 shares, you buy a deep ITM long-dated call (a LEAPS) that acts as a cheaper proxy for the shares, then sell short-dated calls against it. Same concept as a covered call but with less capital tied up. This requires margin most of the time and needs careful handling and if possible, proper order management to ensure that you don't get into a bad position.

**Best expiry to sell options** - when selling premium (CCs, CSPs, spreads), the 21-45 DTE (days to expiration) window is generally considered optimal. This is because theta decay accelerates as you approach expiration, meaning you collect the most time value relative to the risk taken in this window. Going shorter (under 21 DTE) means faster decay but also higher gamma risk, where small stock moves cause big swings in the option price. Most sellers close early at 50% profit rather than holding to expiration, which locks in gains and frees up capital for the next trade.

![Theta Decay Curve](/assets/img/others/theta-decay.png)
_Source: [Option Alpha](https://optionalpha.com/learn/theta)_



### Spreads and Defined Risk Trades

Instead of buying or selling a naked option, you combine two options to cap both your max profit and max loss.

**Vertical spread** - buy one option and sell another at a different strike, same expiration. A bull call spread means buying a call at a lower strike and selling one at a higher strike. Your max gain is the width of the spread minus the premium paid. Your max loss is just the premium. Useful when you have a directional view but want to reduce cost and cap risk.

**Iron Condor** - sell an OTM call spread and an OTM put spread simultaneously. You collect premium from both sides and profit as long as the stock stays within a range by expiration. Popular in low-volatility, range-bound markets. Max loss is if the stock breaks out of either side.

**Iron Butterfly** - similar to a condor but the short strikes are at the same price (usually ATM). Higher premium collected but a narrower profitable range.

For a deeper look at each of these strategies, see [A Deep Dive into Option Trading Strategies](/posts/finance/a-deep-dive-into-option-trading-strategies/).

---

## Tools

**[Option Profit Calculator](https://www.optionsprofitcalculator.com)** - The easiest way to visualize a strategy's P&L at expiration. You can plug in your strikes, contract cost, and expiry and it draws the payoff curve.

**[Market Chameleon](https://marketchameleon.com)** - I usually use this for historical IV charts. The IV rank (IVR) shows in a nice chart where current IV sits relative to its 52-week high and low. IV percentile (IVP) shows the percentage of days in the past year where IV was lower than today.
