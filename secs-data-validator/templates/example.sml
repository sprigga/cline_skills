# SECS-II SML 範例訊息
# 使用 '#' 開頭的行為註解

# S1F1 - Are You There (無 body)
S1F1 W
.

# S1F2 - On Line Data
S1F2
<L
  <A 'MDLN-001'>
  <A '1.0.0'>
>.

# S6F11 - Event Report Send
S6F11 W
<L
  <U4 12345>
  <U4 1>
  <L
    <L
      <U4 101>
      <L
        <U4 1001>
        <U1 255>
      >
    >
  >
>.

# S2F41 - Host Command Send
S2F41 W
<L
  <A 'START'>
  <L
    <L
      <A 'Speed'>
      <U2 100>
    >
    <L
      <A 'Mode'>
      <A 'AUTO'>
    >
  >
>.
