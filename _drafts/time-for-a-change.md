---
layout: post
title: "Time for a Change"
---

Last Friday was my last day at Capital One. I will miss all of the wonderful
people that I had the fortune to work with over the past few years. Next week I
will be joining the Product team at NVIDIA to focus on Python Developer tools.

One habbit that I've picked up during my time a Capital One that I intend to
keep is blogging. I'll start by taking a look back on a few things.

### Dask

When I joined Capital One over two and a half years ago, I was happy to find a
few Dask users had managed to deploy clusters on a few of the internal
infrastructure systems, however it wasn't widely adopted. In fact, a few Python
model training pipelines were scaled vertically on larger cloud instances. These
pipeline swere taking days to run, but the developers wanted to stick with the
PyData stack. This was an opportunity for Dask so I started a side project to
evangelize it at the company. I began giving tutorials to education others on
how the library could help them scale their workflows. Eventually, I was
managing a team of Dask developers and my side project suddenly became one of my
primary duties. We built an internal community of hundreds of Dask users,
contributed to the public project, gave public and internal talks about our
work, training hundreds of data scientists, and even built our own libraries on
top of Dask.

### RAPIDS

A few months into my time at Capital One, the Center for Machine Learning formed
a partnership with the RAPIDS team at NVIDIA. Our goal was to be early testers,
provide feedback, and contribute. Again, deployments were a huge challenge,
however we managed to usher the suite of conda packages and system level
dependencies through the cloud governance policies. Before long we were testing
multi-node, multi-GPU computing workflows and felt the bounds of network
limitations on the cloud. A nice place to be! Additionally, we were on the front
lines of beta users for the incorporation of native Dask support and GPU
acceleration into XGBoost. Lack of efficient GPU development environments
limited our code contributions to the project and ability to support GPU
computing in our internal libraries. My advice is to just build a workstation
and throw a GPU card in it, but even that can be a challenge for a financial
institution.

### Rubicon

I was originally hired to lead the Rubicon team, although back
then it had a completely different architecture that was based on gRPC. We went
through a few major architectural overhaws and eventually landed on a
simplified design that could be open sourced without the need for custom
services. At the same time, we realized how making Rubicon a "serverless"
library, built on top of
[fsspec](https://filesystem-spec.readthedocs.io/en/latest/), could dramatically
reduce our operational burden. I look forward to seeing how the project evolves
and hope it grows in the PyData community.

### Remote Work During a Pandemic

The last fifteen months of working remotely have had its ups and downs. For one,
my home office has had a few major upgrades! I must say that I am so proud of
the team for seamlessly transitioning to being remote full time last year. I
have often stopped to think about how amazing it was to see so many families
pressing on as best as they can during the pandemic. Blurred lines between home
and work, and back-to-back Zoom calls all day, have left me feeling burned out
on a few occasions. Everyone, please remember to take breaks and go for a quick
walk a few times during the day. It is easy to sit at your desk for way too long!

### Being a Middle Aged Programmer in 2020

Building enginneering teams is a lot of fun! Running them is not always as much
fun, but still pretty neat! As a Director at Capital One, I was constantly asked
if I was manager or individual contributor (IC). I would say, "both" or "it
depends on the day." As time wore on, I would spend less time thinking about
code and more time thinking about people who wrote the code. And that was fine
as long as I remained close to the users. Over time, I felt more like a
technical product manager than an engineer. When I started talking to the
Product team at NVIDIA, it was a natural fit!

Being a Director of Software Engineering was all very interesting and I may do
it again someday, but I don't think the path I was on is the only one for this
middle aged programmer. It seems to me that the path I'm about to walk--in the
traversal of tree of life in this profession--should be explored given that
there will be even more middle aged programmers in the not to distant future.
Perhaps more on this later.

### What's Next?

I'm extremely excited to join NVIDIA and help drive the acceleration of the
Python ecosystem. The Python community is amazing and the work has been very
rewarding. For now, I'll be managing products rather than engineers. And perhaps
some mischief from time to time. We will see how it goes.