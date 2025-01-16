library(tidyverse)
library(ellmer)

chat <- chat_openai(
  model = "gpt-4o-mini",
  system_prompt = "You are an expert translator with knowledge of formal language and international diplomacy.",
  api_key = read_lines("cred/open")[1],
  echo = "none"
)

out <- chat$chat("Please provide a precise, fluent, and culturally accurate translation of the following statement from Spanish to English, maintaining the formal tone appropriate for a statement made by a country in an international negotiation context:

Segunda Sesión del Comité Intergubernamental de 
Negociación  
Intervención de la República de Cuba en el Punto 4 de la 
Agenda  
Señor Presidente:  
Agradecemos al Gobierno de Francia por la organización y 
acogida de esta segunda sesión del INC. Asimismo valoramos 
positivamente los trabajos intersesionales que se han realizado 
previo a esta reunión, con un importante apoyo de la 
Secretaría.  
Cuba desea  reiterar que la contaminac ión por plásticos, 
incluyendo  el medio marino, es una problemática heredada 
por los países en desarrollo , desde el punto de vista 
tecnológico y ambiental.  
Con la creación y desarrollo de los plásticos en el mundo, en 
mi país los ecosistemas  se han llenado de basura plástica, sin 
tener ahora todas las condiciones y medios para resolver el 
problema.  Además de tener que enfrentar otras presiones 
como un recrudecido bloqueo económico, comercial y 
financiero que se aplic a a Cuba , por más de 60 años.  
Apoyamos y estamos comprometidos con la elaboración de un 
instrumento jurídicamente vinculante  y ambicioso , pero 
teniendo en cuenta las circunstancias y capacidades de 
los países en desarrollo . También se deberán considerar la s 
consecuencias sociales y económicas que tendrán las 
medidas de control sobre los productos plásticos , en especial 
para aquellos que más contribuyen a la contaminación 
ambiental como son algunos plásticos de un solo uso.  El nivel de ambición y exigencias del nuevo instrumento 
dependerá de que los países en desarrollo puedan recibir de 
manera proporcional medios de implementación, con flujos 
financieros robustos, seguros, adicionales y predecibles; que 
se pueden financiar proyectos I+D+i que incluy an transf erencia 
de tecnologías y se reciba la asistencia técnica y creación de 
capacidades necesarias .  
Recordamos que s egún el mandato de la resolución 
UNEP/EA.5/Res.14 el instrumento debe enfocarse en la 
contaminación por plásticos y no pretender desaparecer a 
estos productos, sin existir alternativas viables y accesibles 
para todos los países .  
Será muy importante y necesario que el nuevo instrumento 
cuente con el enfoque de la gradualidad para alcanzar su 
objetivo  y la implementación de las regul aciones, en función de 
las capacidades nacionales, incluyendo el incremento gradual 
de los compromisos.  
En materia de compromisos globales, se deben priorizar las 
obligaciones, medidas, metas, etc., dirigidas a reducir y 
gradualmente eliminar la contaminac ión por plásticos , 
empleando el enfoque del  ciclo de vida de los productos .  
Destacamos que es una prioridad hacer uso de la ciencia para 
la toma de decisiones, de lo contrario será más complicado 
lograr consenso en temas sustantivos , que incluyen la 
regul ación a aditivos y químicos peligrosos , lo cual deberá 
definirse a partir de evidencias científicas  y criterios bien 
establecidos . 
Se requiere también tener una definición clara dentro del 
instrumento sobre los plástic os problemáticos e innecesarios . No es factible establecer a nivel global un único 
tipo de medida, como por ejemplo la eliminación, para la amplia 
gama de productos que se intenta clasificar en este grupo de 
productos. Entre ellos existen notables diferencias en cuanto 
al us o, manejo de desechos e impactos ambientales y en la 
salud . 
Finalmente, deseamos que los trabajos en esta semana 
permitan dar un impulso importante a las negociaciones, con 
vista a disponer de un primer proyecto de texto para la tercera 
sesión del INC  y de esa manera contribuir a las celebraciones 
del Día Mundial del Medio Ambiente, el próximo 5 de junio, que 
este año se centra en las soluciones a la contaminación por 
plásticos.  
Con los resultados de esta semana de negociación hagamos 
nuestro aporte a la campaña #SinContaminaciónPor Plásticos.  
Muchas gracias.  
")
