"""
Generación del reporte de autenticidad en consola.
"""

from dataclasses import dataclass


@dataclass
class CriterionResult:
    key: str
    label: str
    weight: float
    score: int          # 0-100
    observaciones: str
    image_found: bool


def _bar(score: int, width: int = 30) -> str:
    """Barra de progreso ASCII para el score."""
    filled = int(round(score / 100 * width))
    return "█" * filled + "░" * (width - filled)


def _score_label(score: int) -> str:
    if score >= 80:
        return "✅ ALTO"
    elif score >= 60:
        return "⚠️  MEDIO"
    elif score >= 40:
        return "🔶 BAJO"
    else:
        return "❌ MUY BAJO"


def print_report(results: list[CriterionResult], session_id: str):
    """Imprime el reporte completo en consola."""

    # Calcular score total ponderado (solo criterios con imagen encontrada)
    total_weight = sum(r.weight for r in results if r.image_found)
    if total_weight > 0:
        weighted_score = sum(
            r.score * r.weight for r in results if r.image_found
        ) / total_weight
    else:
        weighted_score = 0

    final_score = round(weighted_score)

    # ── Header ──────────────────────────────────────────────────────────────
    print()
    print("=" * 62)
    print("  AUTHSCORE — REPORTE DE AUTENTICIDAD GUCCI")
    print(f"  Sesión: {session_id}")
    print("=" * 62)

    # ── Score global ────────────────────────────────────────────────────────
    print()
    print(f"  SCORE FINAL: {final_score}/100  {_score_label(final_score)}")
    print(f"  {_bar(final_score, 40)}")
    print()

    if final_score >= 80:
        verdict = "Alta probabilidad de autenticidad. El producto supera los umbrales en la mayoría de criterios."
    elif final_score >= 60:
        verdict = "Autenticidad probable con reservas. Algunos criterios requieren revisión adicional."
    elif final_score >= 40:
        verdict = "Autenticidad dudosa. Múltiples criterios presentan señales de alerta."
    else:
        verdict = "Alta probabilidad de falsificación. El producto no supera los criterios básicos de autenticidad."

    print(f"  Interpretación: {verdict}")
    print()

    # ── Desglose por criterio ───────────────────────────────────────────────
    print("─" * 62)
    print("  DESGLOSE POR CRITERIO")
    print("─" * 62)

    for r in results:
        print()
        if not r.image_found:
            print(f"  [{r.label}]")
            print(f"  ⚫ Foto no encontrada — criterio excluido del score")
            continue

        pct_contribution = round(r.score * r.weight / total_weight) if total_weight > 0 else 0

        print(f"  [{r.label}]  Peso: {int(r.weight * 100)}%")
        print(f"  Score: {r.score}/100  {_bar(r.score, 25)}  {_score_label(r.score)}")
        print(f"  Contribución al total: ~{pct_contribution} puntos")
        print(f"  Obs: {r.observaciones}")

    # ── Disclaimer ──────────────────────────────────────────────────────────
    print()
    print("─" * 62)
    print("  ⚠  AVISO LEGAL")
    print("─" * 62)
    print(
        "  Este score es un indicador probabilístico generado por IA.\n"
        "  No constituye una certificación de autenticidad garantizada.\n"
        "  AuthScore no asume responsabilidad por decisiones tomadas\n"
        "  exclusivamente en base a este análisis."
    )
    print("=" * 62)
    print()
