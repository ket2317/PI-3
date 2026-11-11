from datetime import date, datetime
from io import BytesIO
from zoneinfo import ZoneInfo

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ZONA = ZoneInfo("America/Mexico_City")
VINO = colors.HexColor("#7a3038")  # color principal de Vendora
GRIS = colors.HexColor("#64748b")
BORDE = colors.HexColor("#e5eaf2")
FONDO = colors.HexColor("#f6f2ec")


def dinero(valor) -> str:
    return f"${float(valor):,.2f}"


def texto_periodo(desde: date | None, hasta: date | None) -> str:
    if desde and hasta:
        return f"Del {desde:%d/%m/%Y} al {hasta:%d/%m/%Y}"
    if desde:
        return f"Desde el {desde:%d/%m/%Y}"
    if hasta:
        return f"Hasta el {hasta:%d/%m/%Y}"
    return "Todo el periodo"


def tabla(filas: list[list], anchos: list[float], columnas_numericas: int = 0) -> Table:
    """Tabla con encabezado de color y renglones alternados.

    columnas_numericas: cuántas columnas del final se alinean a la derecha.
    """
    t = Table(filas, colWidths=anchos, repeatRows=1)
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), VINO),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FONDO]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, BORDE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if columnas_numericas:
        estilo.append(("ALIGN", (-columnas_numericas, 0), (-1, -1), "RIGHT"))
    t.setStyle(TableStyle(estilo))
    return t


def generar_pdf_ventas(
    estadisticas: dict,
    ventas: list[dict],
    desde: date | None,
    hasta: date | None,
    generado_por: str,
) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=1.6 * cm,
        rightMargin=1.6 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title="Reporte de ventas - Vendora",
    )

    estilos = getSampleStyleSheet()
    titulo = ParagraphStyle("titulo", parent=estilos["Title"], textColor=VINO, alignment=0)
    subtitulo = ParagraphStyle("subtitulo", parent=estilos["Heading2"], textColor=VINO, spaceBefore=14)
    nota = ParagraphStyle("nota", parent=estilos["Normal"], textColor=GRIS, fontSize=9)

    ahora = datetime.now(ZONA)
    contenido = [
        Paragraph("Reporte de ventas", titulo),
        Paragraph(
            f"{texto_periodo(desde, hasta)} &nbsp;·&nbsp; Generado el {ahora:%d/%m/%Y %H:%M} "
            f"por {generado_por}",
            nota,
        ),
        Spacer(1, 12),
    ]

    # 1. Resumen: total, número de ventas y ticket promedio
    resumen = Table(
        [
            ["Total vendido", "Número de ventas", "Ticket promedio"],
            [
                dinero(estadisticas["total_vendido"]),
                str(estadisticas["numero_ventas"]),
                dinero(estadisticas["ticket_promedio"]),
            ],
        ],
        colWidths=[6 * cm] * 3,
    )
    resumen.setStyle(
        TableStyle(
            [
                ("TEXTCOLOR", (0, 0), (-1, 0), GRIS),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 1), (-1, 1), 16),
                # LEADING = alto de la línea; si no se sube junto con FONTSIZE el número se corta
                ("LEADING", (0, 1), (-1, 1), 20),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 10),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("BOX", (0, 0), (-1, -1), 0.5, BORDE),
                ("BACKGROUND", (0, 0), (-1, -1), FONDO),
            ]
        )
    )
    contenido.append(resumen)

    # 2. Productos más vendidos
    contenido.append(Paragraph("Productos más vendidos", subtitulo))
    filas = [["Producto", "Código", "Piezas", "Importe"]]
    for p in estadisticas["productos_mas_vendidos"]:
        filas.append([p["nombre"], p["codigo"], p["cantidad_vendida"], dinero(p["importe"])])
    if len(filas) == 1:
        filas.append(["Sin ventas en este periodo", "", "", ""])
    contenido.append(tabla(filas, [7.5 * cm, 4 * cm, 2.5 * cm, 4 * cm], columnas_numericas=2))

    # 3. Ventas por sucursal
    contenido.append(Paragraph("Ventas por sucursal", subtitulo))
    filas = [["Sucursal", "Ventas", "Total"]]
    for s in estadisticas["ventas_por_sucursal"]:
        filas.append([s["sucursal"], s["numero_ventas"], dinero(s["total"])])
    if len(filas) == 1:
        filas.append(["Sin ventas en este periodo", "", ""])
    contenido.append(tabla(filas, [10 * cm, 3.5 * cm, 4.5 * cm], columnas_numericas=2))

    # 4. Detalle de cada venta
    contenido.append(Paragraph(f"Detalle de ventas ({len(ventas)})", subtitulo))
    filas = [["Venta", "Fecha", "Sucursal", "Cajero", "Pago", "Total"]]
    for v in ventas:
        fecha = v["created_at"].astimezone(ZONA).strftime("%d/%m/%Y %H:%M")
        filas.append(
            [f"#{v['id']}", fecha, v["sucursal"], v["usuario"], v["metodo_pago"], dinero(v["total"])]
        )
    if len(filas) == 1:
        filas.append(["", "Sin ventas en este periodo", "", "", "", ""])
    contenido.append(
        tabla(filas, [1.6 * cm, 3 * cm, 3.6 * cm, 3.6 * cm, 3 * cm, 3.2 * cm], columnas_numericas=1)
    )

    # Número de página al pie de cada hoja
    def pie(canvas, documento):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(GRIS)
        canvas.drawRightString(letter[0] - 1.6 * cm, 1 * cm, f"Página {documento.page}")
        canvas.drawString(1.6 * cm, 1 * cm, "Vendora · Reporte de ventas")
        canvas.restoreState()

    doc.build(contenido, onFirstPage=pie, onLaterPages=pie)
    return buffer.getvalue()
