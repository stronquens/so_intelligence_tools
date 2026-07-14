import flagAr from "flag-icons/flags/4x3/sa.svg";
import flagCa from "flag-icons/flags/4x3/es-ct.svg";
import flagDe from "flag-icons/flags/4x3/de.svg";
import flagEn from "flag-icons/flags/4x3/us.svg";
import flagEs from "flag-icons/flags/4x3/es.svg";
import flagEu from "flag-icons/flags/4x3/es-pv.svg";
import flagFr from "flag-icons/flags/4x3/fr.svg";
import flagGl from "flag-icons/flags/4x3/es-ga.svg";
import flagHi from "flag-icons/flags/4x3/in.svg";
import flagIt from "flag-icons/flags/4x3/it.svg";
import flagJa from "flag-icons/flags/4x3/jp.svg";
import flagKo from "flag-icons/flags/4x3/kr.svg";
import flagNl from "flag-icons/flags/4x3/nl.svg";
import flagPl from "flag-icons/flags/4x3/pl.svg";
import flagPt from "flag-icons/flags/4x3/pt.svg";
import flagRu from "flag-icons/flags/4x3/ru.svg";
import flagUk from "flag-icons/flags/4x3/ua.svg";
import flagUn from "flag-icons/flags/4x3/un.svg";
import flagZh from "flag-icons/flags/4x3/cn.svg";

const flagByLanguage: Record<string, string> = {
  ar: flagAr,
  ca: flagCa,
  de: flagDe,
  en: flagEn,
  es: flagEs,
  eu: flagEu,
  fr: flagFr,
  gl: flagGl,
  hi: flagHi,
  it: flagIt,
  ja: flagJa,
  ko: flagKo,
  nl: flagNl,
  pl: flagPl,
  pt: flagPt,
  ru: flagRu,
  uk: flagUk,
  zh: flagZh,
};

export function flagUrl(code: string): string {
  return flagByLanguage[code] ?? flagUn;
}
