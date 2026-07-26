---
layout: post
title: "Buyout Rumors and Far OTM Calls"
description: >-
  Why buying deep out-of-the-money calls on companies that might get bought out is a bad idea.
author: ryo
date: 2026-07-26 20:01:20 +0800
categories: [Finance]
tags: [finance, stocks, options]
toc: true
comments: true
pin: false
published: true
---

## Overview

Why buying far out-of-the-money (OTM) calls on companies that could realistically get bought out is a bad idea.

---

## My PayPal Position

I bought a **PayPal (PYPL) $90 strike call expiring December 15, 2028**, when PayPal was trading around $45. This was a LEAPS call, far OTM, with over 2 years to expiry, meant to give the stock room to run without fast theta decay.

Buyout news then came out, reporting a potential acquisition in the ballpark of **$60 per share**. PayPal never agreed to anything. The call then dropped **60%**.

The rumored buyout price was *higher* than where the stock was already trading before the news, which in theory should be bullish. The stock did react, jumping from **$45 to $55**. Despite that, the $90 strike call still lost most of its value.

---

## Why This Happens

The issue is implied volatility (IV) and what a buyout does to it.

Before the news, the $90 call had a real, if small, chance of finishing ITM, priced on normal stock volatility over 2+ years. Plenty of room to eventually reach $90 given enough time and uncertainty. That uncertainty is what a LEAPS call's extrinsic value is priced on.

The moment a buyout at $60 is on the table, that uncertainty collapses. If a deal happens, the stock is capped at (or very near) the deal price. There's no more scenario where it organically runs to $90 by 2028, because if the deal closes, the stock stops trading and gets absorbed at $60. The chance of a big speculative move upward, the entire reason to hold the option, gets priced out almost instantly.

This is called IV crush, but more severe than the earnings kind. Earnings IV crush resolves uncertainty for a day. Buyout IV crush resolves uncertainty for the rest of the option's life. A 2028 dated call has years of "maybe it moons" priced in. A buyout removes that "maybe" completely.

---

## Why the Stock Only Went to $55, Not $60

The stock rose to $55 and stayed there, a few dollars below the rumored $60 deal price. This gap is priced deal risk, and it's the entire business model of **merger arbitrage funds**.

When a buyout is announced or rumored, the target stock typically trades at a discount to the deal price. That discount reflects:

- **Deal completion risk** - will this actually close, or fall through (regulatory blocks, financing, shareholder votes, or here, PayPal never even agreeing to anything)
- **Time value of money** - capital is locked up until close, which could be 12-18 months out
- **General market risk** - things can happen between now and close that affect sentiment

Merger arb funds buy the stock at the discount ($55) and bet the deal closes at the higher price ($60), pocketing the spread. A confirmed, signed deal at $60 would trade closer to $58-59, reflecting low risk and just the time value of waiting. Landing at only $55 signals real doubt the deal happens at all, consistent with PayPal never confirming anything. If the deal falls apart, the stock reverts back toward pre-rumor levels, or lower. That's the risk merger arb funds get paid to take.

---

## Two Very Different Bets

A far OTM LEAPS call is a bet on **organic growth far beyond any realistic near-term outcome**. Merger arb is a bet on **deal completion at a known price close to the current one**. Nearly opposite trades:

| | PYPL $90C 2028 | Merger Arb Position |
|---|---|---|
| Bet | Stock organically runs past $90 | Deal closes near announced price |
| Time horizon | 2+ years, needs sustained upside | Weeks to ~18 months, defined catalyst |
| Effect of a buyout | Kills it (caps upside, crushes IV) | Is the entire thesis |
| Max gain | Theoretically unlimited | Capped at the spread to deal price |
| Max loss | 100% of premium | Deal breaks, stock drops back down |

The moment a buyout became plausible, these two positions became mutually exclusive. Merger arb's edge comes precisely from situations where the far OTM call gets wrecked.

---

## The Lesson

Before holding far OTM LEAPS calls, we should always consider what happens to the position if the company gets acquired at a price below the strike. If there are weird signs that might point to a possible buyout soon, like price spikes or unusual operation activity, it might be best to hold off.