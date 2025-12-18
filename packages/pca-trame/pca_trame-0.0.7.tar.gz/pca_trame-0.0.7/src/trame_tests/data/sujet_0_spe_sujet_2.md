
```yaml
part_1:
  question_1:
    statement: "On considère l'arbre de probabilité ci-contre. On cherche la probabilité de l'évènement $B$. On a :"
    choices:
      a: "$p(B)=0,18$"
      b: "$p(B)=0,12$"
      c: "$p(B)=0,66$"
      d: "$p(B)=0,3$"
    correct_answer: "c"
  question_2:
    statement: "Une tablette coûte 200 euros. Son prix diminue de $30 \\%$. Le prix après cette diminution est :"
    choices:
      a: "$140$ euros"
      b: "$170$ euros"
      c: "$194$ euros"
      d: "$197$ euros"
    correct_answer: "a"
  question_3:
    statement: "Une réduction de $50 \\%$ suivie d'une augmentation de $50 \\%$ équivaut à :"
    choices:
      a: "une réduction de $50 \\%$"
      b: "une réduction de $25 \\%$"
      c: "une augmentation de $25 \\%$"
      d: "une augmentation de $75 \\%$"
    correct_answer: "b"
  question_4:
    statement: "Dans un lycée, le quart des élèves sont internes, parmi eux, la moitié sont des filles. La proportion des filles internes par rapport à l'ensemble des élèves du lycée est égale à :"
    choices:
      a: "$4 \\%$"
      b: "$12,5 \\%$"
      c: "$25 \\%$"
      d: "$50 \\%$"
    correct_answer: "b"
  question_5:
    statement: "On considère le nombre $N=\\dfrac{10^{7}}{5^{2}}$. On a :"
    choices:
      a: "$N=2^{5}$"
      b: "$N=20000$"
      c: "$N=\\dfrac{1}{10^{5}}$"
      d: "$N=4 \\times 10^{5}$"
    correct_answer: "d"
  question_6:
    statement: "Un appareil a besoin d'une énergie de $7,5 \\times 10^{6}$ Joules (J) pour se mettre en route. À combien de kiloWatts-heure ( kWh ) cela correspond-il ? Données : $1 \\mathrm{kWh}=3,6 \\times 10^{6} \\mathrm{~J}$."
    choices:
      a: "$0,5 \\mathrm{kWh}$"
      b: "$2,08 \\mathrm{kWh}$"
      c: "$5,3 \\mathrm{kWh}$"
      d: "$20,35 \\mathrm{kWh}$"
    correct_answer: "b"
  question_7:
    statement: "Le plan est muni d'un repère orthogonal. On note $d$ la droite passant par les points $A(0 ;-1)$ et $B(2 ; 5)$. Le coefficient directeur de la droite $d$ est égal à :"
    choices:
      a: "$-\\dfrac{1}{2}$"
      b: "$2$"
      c: "$3$"
      d: "$\\dfrac{1}{3}$"
    correct_answer: "c"
  question_8:
    statement: "On a représenté ci-contre une droite $D$. Parmi les quatre équations ci-dessous, la seule susceptible de représenter la droite $D$ est :"
    choices:
      a: "$2 x-y=0$"
      b: "$2 x+y+1=0$"
      c: "$y=x^{2}-(x+1)^{2}+1$"
      d: "$y=2 x-1$"
    correct_answer: "d"
  question_9:
    statement: "On note $S$ l'ensemble des solutions de l'équation $x^{2}=10$ sur $\\mathbb{R}$. On a :"
    choices:
      a: "$S=\\{-5 ; 5\\}$"
      b: "$S=\\{-\\sqrt{5} ; \\sqrt{5}\\}$"
      c: "$S=\\{-\\sqrt{10} ; \\sqrt{10}\\}$"
      d: "$S=\\emptyset$"
    correct_answer: "c"
  question_10:
    statement: "La fonction $f$ définie sur $\\mathbb{R}$ par $f(x)=(3 x-15)(x+2)$ admet pour tableau de signes :"
    choices:
      a: "Tableau A"
      b: "Tableau B"
      c: "Tableau C"
      d: "Tableau D"
    correct_answer: "a"
  question_11:
    statement: "L'expression développée de $(2 x+0,5)^{2}$ est :"
    choices:
      a: "$4 x^{2}+x+0,25$"
      b: "$4 x^{2}+4 x+2$"
      c: "$4 x^{2}+2 x+0,25$"
      d: "$4 x^{2}+2 x+1$"
    correct_answer: "c"
  question_12:
    statement: "Lorsqu'un point mobile suit une trajectoire circulaire de rayon $R$, en mètre (m), son accélération centripète $a$ (en $\\mathrm{m} / \\mathrm{s}^{2}$ ) s'exprime en fonction de la vitesse $v$ (en $\\mathrm{m} / \\mathrm{s}$ ) de la manière suivante : $a=\\dfrac{v^{2}}{R}$. L'expression permettant, à partir de cette formule, d'exprimer la vitesse $v$ est :"
    choices:
      a: "$v=a R^{2}$"
      b: "$v=\\sqrt{a R}$"
      c: "$v=\\sqrt{\\dfrac{a}{R}}$"
      d: "$v=\\dfrac{a^{2}}{R}$"
    correct_answer: "b"
part_2:
  exercise_1:
    statement: "En 2020, une ville comptait 10000 habitants. On modélise l'évolution du nombre d'habitants de cette ville par la suite ( $u_{n}$ ) définie ainsi :"
    data:
      - "u_{n+1}=1,08 u_{n}-300, n ∈ ℕ"
      - "u_{0}=10000"
    questions:
      - 1:
          statement: "Indiquer ce que représente $u_{1}$ et calculer sa valeur."
          answer: "$u_{1}$ représente le nombre d'habitants en 2021 et sa valeur est 10500."
      - 2.a:
          statement: "Déterminer $v_{0}$."
          answer: 6250
        2.b:
          statement: "Démontrer que pour tout entier naturel $n$, on a $v_{n+1}=1,08 v_{n}$."
          answer: "Démonstration effectuée."
        2.c:
          statement: "En déduire la nature de la suite $\\left(v_{n}\\right)$."
          answer: "Suite géométrique de raison 1.08."
        2.d:
          statement: "Pour tout entier naturel $n$, exprimer, $v_{n}$ en fonction de $n$."
          answer: "$v_{n} = 6250 \\times 1.08^{n}$"
        2.e:
          statement: "En déduire que pour tout entier naturel $n$, on a $u_{n}=6250 \\times 1,08^{n}+3750$."
          answer: "Expression déduite."
      - 3:
          statement: "La municipalité envisage d'ouvrir une nouvelle école maternelle dès que la population atteindra 19000 habitants. La construction d'un tel établissement nécessitant deux ans, déterminer l'année à partir de laquelle la construction de l'école doit commencer."
          answer: "2030"
  exercise_2:
    statement: "Le plan est muni d'un repère orthogonal."
    partie_a:
      - 1.a:
          statement: "Déterminer les racines de $P$."
          answer: "Les racines sont $x = -2.5$ et $x = 2$."
        1.b:
          statement: "En déduire l'axe de symétrie de la parabole d'équation $y=P(x)$."
          answer: "$x = -0.25$"
      - 2:
          statement: "Établir le tableau de signe de la fonction $P$ sur l'intervalle $[-5 ; 3]$."
          answer:
            intervals:
              - "x ∈ [-5; -2.5]: P(x) > 0"
              - "x ∈ [-2.5; 2]: P(x) < 0"
              - "x ∈ [2; 3]: P(x) > 0"
    partie_b:
      - 1:
          statement: "Donner la valeur du nombre dérivé $f^{\\prime}(2)$."
          answer: 0
      - 2:
          statement: "Résoudre, avec la précision permise par le graphique, l'inéquation $f^{\\prime}(x)<0$."
          answer: "Résolution effectuée."
      - 3:
          statement: "Démontrer que, pour tout $x$ appartenant à l'intervalle $[-5 ; 3]$, on a $f^{\\prime}(x)=P(x) \\mathrm{e}^{0,5 x}$."
          answer: "Démonstration effectuée."
      - 4:
          statement: "En utilisant les résultats de la partie A, dresser le tableau de variation de la fonction $f$ sur l'intervalle $[-5 ; 3]$."
          answer:
            intervals:
              - "x ∈ [-5; -2.5]: f croissante"
              - "x ∈ [-2.5; 2]: f décroissante"
              - "x ∈ [2; 3]: f croissante"
```