

```yaml
part_1:
  question_1:
    statement: "L'inverse du double de $5$ est égal à :"
    choices:
      a: "$\\dfrac{2}{5}$"
      b: "$\\dfrac{1}{10}$"
      c: "$\\dfrac{5}{2}$"
      d: "$10$"
    correct_answer: "b"
  question_2:
    statement: "On considère la relation $F=a+\\dfrac{b}{c d}$. Lorsque $a=\\dfrac{1}{2}, \\ b=3, \\ c=4, \\ d=-\\dfrac{1}{4}$, la valeur de $F$ est égale à :"
    choices:
      a: "$-\\dfrac{5}{2}$"
      b: "$-\\dfrac{3}{2}$"
      c: "$\\dfrac{5}{2}$"
      d: "$\\dfrac{3}{2}$"
    correct_answer: "a"
  question_3:
    statement: "Le prix d'un article est multiplié par $0,975$. Cela signifie que le prix de cet article a connu :"
    choices:
      a: "une baisse de $2,5 \\%$"
      b: "une augmentation de $97,5 \\%$"
      c: "une baisse de $25 \\%$"
      d: "une augmentation de $0,975 \\%$"
    correct_answer: "a"
  question_4:
    statement: "Le prix d'un article est noté $P$. Ce prix augmente de $10 \\%$ puis baisse de $10 \\%$. A l'issue de ces deux variations, le nouveau prix est noté $P_{1}$. On peut affirmer que :"
    choices:
      a: "$P_{1}=P$"
      b: "$P_{1}>P$"
      c: "$P_{1} < P$"
      d: "Cela dépend de $P$"
    correct_answer: "c"
  question_5:
    statement: "On lance un dé à $4$ faces. La probabilité d'obtenir chacune des faces est donnée dans le tableau ci-dessous :"
    table:
      face_1: "$0,5$" 
      face_2: "$\\dfrac{1}{6}$"
      face_3: "$0,2$"
      face_4: "$x$"
    question: "On peut affirmer que :" # NOTE mad: looks like a mistake to me, I commented it out
    choices:
      a: "$x=\\dfrac{2}{15}$"
      b: "$x=\\dfrac{2}{3}$"
      c: "$x=0,4$"
      d: "$x=0,1$"
    correct_answer: "a"
  question_6:
    statement: "On considère $x, y, u$ des réels non nuls tels que $\\dfrac{1}{x}+\\dfrac{1}{y}=\\dfrac{1}{u}$. On peut affirmer que :"
    choices:
      a: "$u=\\dfrac{x y}{x+y}$"
      b: "$u=\\dfrac{x+y}{x y}$"
      c: "$u=x y$"
      d: "$u=x+y$"
    correct_answer: "a"
  question_7:
    statement: "On a représenté ci-contre la parabole d'équation $y=x^{2}$. On note $(7)$ l'inéquation, sur $\\mathbf{R}, x^{2} \\geq 10$. L'inéquation $(7)$ est équivalente à :"
    choices:
      a: "$-\\sqrt{10} \\leq x \\leq \\sqrt{10}$"
      b: "$x \\leq-\\sqrt{10}$ ou $x \\geq \\sqrt{10}$"
      c: "$x \\geq \\sqrt{10}$"
      d: "$x=\\sqrt{10}$ ou $x=-\\sqrt{10}$"
    correct_answer: "b"
  question_8:
    statement: "On a représenté ci-contre une droite $\\mathcal{D}$ dans un repère orthonormé. Une équation de la droite $\\mathcal{D}$ est :"
    choices:
      a: "$y=-\\dfrac{3}{2} x+2$"
      b: "$y=\\dfrac{2}{3} x+2$"
      c: "$2 x-3 y-6=0$"
      d: "$\\dfrac{x}{3}+\\dfrac{y}{2}-1=0$"
    correct_answer: "d"
  question_9:
    statement: "On considère trois fonctions définies sur $\\mathbf{R}$ :"
    fonctions:
      - "$f_{1}: x \\mapsto x^{2}-(1-x)^{2}$"
      - "$f_{2}: x \\mapsto \\dfrac{x}{2}-\\left(1+\\dfrac{1}{\\sqrt{2}}\\right)$"
      - "$f_{3}: x \\mapsto \\dfrac{5-\\dfrac{2}{3} x}{0,7}$"
    question: "Parmi ces trois fonctions, celles qui sont des fonctions affines sont :"
    choices:
      a: "aucune"
      b: "toutes"
      c: "uniquement la fonction $f_{1}$"
      d: "uniquement les fonctions $f_{2}$ et $f_{3}$"
    correct_answer: "b"
  question_10:
    statement: "On a représenté ci-contre une parabole $\\mathcal{P}$. Une seule des quatre fonctions ci-dessous est susceptible d'être représentée par la parabole $\\mathcal{P}$. Laquelle?"
    choices:
      a: "$x \\mapsto x^{2}-10$"
      b: "$x \\mapsto -x^{2}-10$"
      c: "$x \\mapsto -x^{2}+10$"
      d: "$x \\mapsto -x^{2}+10 x$"
    correct_answer: "c"
  question_11:
    statement: "On a représenté ci-contre la courbe $\\mathcal{C}$ d'une fonction $f$. Les points $A, B, R$ et $S$ appartiennent à la courbe $\\mathcal{C}$. Leurs abscisses sont notées respectivement $x_{A}, x_{B}, x_{R}$ et $x_{S}$. L'inéquation $x \\times f(x)>0$ est vérifiée par :"
    choices:
      a: "$x_{A}$ et $x_{B}$"
      b: "$x_{A}$ et $x_{R}$"
      c: "$x_{A}$ et $x_{S}$"
      d: "$x_{A}, x_{B}$ et $x_{S}$"
    correct_answer: "b"
  question_12:
    statement: "Voici une série de notes avec les coefficients associés."
    table:
      note: 
        - $10$
        - $8$
        - $16$
      coefficient: 
        - $1$
        - $2$
        - $x$
    question: "On note $m$ la moyenne de cette série. Que doit valoir $x$ pour que $m=15$ ?"
    choices:
      a: "impossible"
      b: "$x=10^{-3}$"
      c: "$x=3$"
      d: "$x=19$"
    correct_answer: "d"
part_2:
  exercise_1:
    statement: "On considère la figure suivante, représentée dans un repère orthonormé $(0 ; \\vec{\\imath} ; \\vec{\\jmath})$. On dispose des données suivantes :"
    data:
      - "Le quadrilatère $O A B C$ est un carré de côté 4 ;"
      - "On a $A(4 ; 0), B(4 ; 4), C(0 ; 4), I(4 ; 3)$ ;"
      - "Le point $H$ est le projeté orthogonal du point $C$ sur la droite (OI) ;"
      - "On note $\\mathcal{E}$ le cercle de centre $D(2 ; 2)$ et de rayon 0.5."
    questions:
      - 1.a:
          statement: "Déterminer les coordonnées des vecteurs $\\overrightarrow{O I}$ et $\\overrightarrow{O C}$."
          answer:
            oi: "(4, 3)"
            oc: "(0, 4)"
        1.b:
          statement: "En déduire le produit scalaire $\\overrightarrow{O I} \\cdot \\overrightarrow{O C}$."
          answer: 12
      - 2.a:
          statement: "Exprimer le produit scalaire $\\overrightarrow{O I} \\cdot \\overrightarrow{O C}$ en fonction des longueurs $O H$ et $O I$."
          answer: "\\overrightarrow{OI} \\cdot \\overrightarrow{OC} = OI \\times OH"
        2.b:
          statement: "Calculer la longueur $O I$."
          answer: 5
        2.c:
          statement: "En déduire que $O H=2,4$."
          answer: 2.4
      - 3.a:
          statement: "Déterminer une équation cartésienne de la droite $(C H)$."
          answer: "$4x + 3y - 12 = 0$"
        3.b:
          statement: "Justifier qu'une équation du cercle $\\mathcal{E}$ est :"
          equation: "$x^{2}+y^{2}-4 x-4 y+7,75=0$"
          answer: "L'équation est correcte."
        3.c:
          statement: "Le point $M(1,5 ; 2)$ appartient-il à l'intersection du cercle $\\mathcal{E}$ et de la droite $(C H)$ ? Justifier."
          answer: "Oui"
  exercise_2:
    statement: "On se place dans un repère $(0 ; \\vec{\\imath} ; \\vec{\\jmath})$ orthogonal."
    questions:
      - 1.a:
          statement: "On considère la fonction $g$ définie pour tout réel $x$ par $g(x)=x^{2}-5 x+4$. Étudier le signe de la fonction $g$ sur $\\mathbf{R}$."
          answer:
            positive: "x < 1 ou x > 4"
            negative: "1 < x < 4"
            zero: "x = 1 ou x = 4"
        1.b:
          statement: "On considère un entier naturel $n$ quelconque. On note $A_{n}$ le point de la courbe $\\mathcal{P}$ d'abscisse $n$. On note $a_{n}$ le coefficient directeur de la droite $(A_{n} A_{n+1})$. Justifier que pour tout entier naturel $n$, on a $a_{n}=2 n-4$."
          answer: "$a_n = 2n - 4$"
        1.c:
          statement: "Quelle est la nature de la suite $(a_{n})$ ?"
          answer: "Suite arithmétique de raison 2"
      - 2.a:
          statement: "On considère la fonction $f$ définie pour tout réel $x$ de l'intervalle $[0,5 ; 8]$ par $f(x)=x-5+\\dfrac{4}{x}$. Vérifier que pour tout réel $x$, de l'intervalle $[0,5 ; 8]$ on a $f(x)=\\dfrac{g(x)}{x}$."
          answer: "L'égalité est vérifiée."
        2.b:
          statement: "À l'aide de la question 1.a, déterminer la position de la courbe $\\mathcal{C}$ par rapport à l'axe des abscisses."
          answer:
            positive: "0.5 ≤ x < 1 et 4 < x ≤ 8"
            negative: "1 < x < 4"
            zero: "x = 1 ou x = 4"
        2.c:
          statement: "Montrer que pour tout réel $x$ de l'intervalle $[0,5 ; 8]$ on a : $f'(x)=\\dfrac{(x-2)(x+2)}{x^{2}}$."
          answer: "L'égalité est vérifiée."
        2.d:
          statement: "En déduire le tableau de variations de la fonction $f$ sur l'intervalle $[0,5 ; 8]$."
          answer:
            decreasing: "0.5 ≤ x ≤ 2"
            increasing: "2 ≤ x ≤ 8"
            minimum: "x = 2, f(2) = -1"
        2.e:
          statement: "Réaliser un schéma de l'allure de la courbe $\\mathcal{C}$ sur lequel apparaîtront les résultats des questions 2.b et 2.d."
          answer: "Schéma à réaliser"
```