import os
import json
import urllib.request
import asyncio
import flet as ft
from flet.app import run

# ==============================================================================
# CONFIGURACIÓN DE RUTAS Y REPOSITORIO REMOTO
# ==============================================================================
GITHUB_USER = "mikicolmena"
GITHUB_REPO = "Secret-Stories"
GITHUB_BRANCH = "main"

URL_STORIES_REMOTO = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/stories.json"
URL_ASSETS_REMOTO = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/assets/"

# Ruta absoluta dinámica para compatibilidad con Android / Linux / Windows
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_STORIES_LOCAL = os.path.join(BASE_DIR, "stories.json")

def main(page: ft.Page):
    page.title = "Secret Stories"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    bg_color_actual = "#121212"
    page.bgcolor = bg_color_actual
    
    modo_remoto = False
    datos_paquetes = []
    estado_sincronizacion = "Cargando copia local..."
    sincronizando = False

    # --- RESOLVER RUTA DE IMAGEN ---
    def resolver_ruta_imagen(ruta: str) -> str:
        if not ruta:
            return ""
        if ruta.startswith("http://") or ruta.startswith("https://"):
            return ruta
        
        nombre_archivo = ruta.replace("assets/", "", 1) if ruta.startswith("assets/") else ruta
        
        if modo_remoto:
            return f"{URL_ASSETS_REMOTO}{nombre_archivo}"
        return f"/{nombre_archivo}"

    # --- FUNCIÓN DE NAVEGACIÓN ---
    def ir_a(ruta: str):
        page.route = ruta
        route_change(None)

    # --- CAMBIO DE TEMA CLARO / OSCURO ---
    def cambiar_tema(e):
        nonlocal bg_color_actual
        if page.theme_mode == ft.ThemeMode.DARK:
            page.theme_mode = ft.ThemeMode.LIGHT
            bg_color_actual = "#F5F5F5"
        else:
            page.theme_mode = ft.ThemeMode.DARK
            bg_color_actual = "#121212"
        page.bgcolor = bg_color_actual
        route_change(None)

    # --- 1. CARGA LOCAL INICIAL (OFFLINE-FIRST) ---
    def cargar_historias_local():
        nonlocal datos_paquetes, modo_remoto, estado_sincronizacion
        modo_remoto = False
        try:
            if os.path.exists(RUTA_STORIES_LOCAL):
                with open(RUTA_STORIES_LOCAL, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    datos_paquetes = content.get("paquetes", [])
                    estado_sincronizacion = "Cargado desde almacenamiento local"
            else:
                datos_paquetes = []
                estado_sincronizacion = "Sin archivo local de historias"
        except Exception as err:
            datos_paquetes = []
            estado_sincronizacion = f"Error al cargar copia local: {err}"

    # Carga local inmediata antes de mostrar la UI
    cargar_historias_local()

    # --- 2. SINCRONIZACIÓN EN SEGUNDO PLANO ---
    async def sincronizar_github():
        nonlocal datos_paquetes, modo_remoto, estado_sincronizacion, sincronizando
        sincronizando = True
        estado_sincronizacion = "Comprobando historias en la nube..."
        if page.route == "/":
            route_change(None)

        def realizar_peticion():
            try:
                req = urllib.request.Request(URL_STORIES_REMOTO, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=4) as response:
                    return json.loads(response.read().decode('utf-8'))
            except Exception:
                return None

        content_remoto = await asyncio.to_thread(realizar_peticion)
        sincronizando = False

        if content_remoto and "paquetes" in content_remoto:
            paquetes_remotos = content_remoto.get("paquetes", [])
            # Solo actualizamos si hay historias nuevas o cambios reales
            if paquetes_remotos != datos_paquetes:
                datos_paquetes = paquetes_remotos
                modo_remoto = True
                estado_sincronizacion = "¡Nuevas historias cargadas desde GitHub!"
                try:
                    with open(RUTA_STORIES_LOCAL, "w", encoding="utf-8") as f:
                        json.dump(content_remoto, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"No se pudo guardar la copia local: {e}")
            else:
                modo_remoto = True
                estado_sincronizacion = "Conectado: Historias al día"
        else:
            modo_remoto = False
            estado_sincronizacion = "Sin conexión (modo local activo)"

        if page.route == "/":
            route_change(None)

    # Lanza la sincronización sin bloquear la app
    asyncio.create_task(sincronizar_github())

    # --- VISTA 1: MENÚ DE COLECCIONES ---
    def vista_colecciones():
        es_oscuro = (page.theme_mode == ft.ThemeMode.DARK)
        bg_card = "#1E1E1E" if es_oscuro else "#FFFFFF"
        texto_principal = "white" if es_oscuro else "black"
        texto_secundario = "white70" if es_oscuro else "black54"

        controles = [
            ft.Container(
                content=ft.Row(
                    [
                        ft.Container(width=48),
                        ft.Column(
                            [
                                ft.Text("Secret Stories", size=32, weight=ft.FontWeight.BOLD, color="#D32F2F", text_align=ft.TextAlign.CENTER),
                                ft.Text("Selecciona una Colección", size=16, color=texto_secundario, text_align=ft.TextAlign.CENTER),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.LIGHT_MODE if es_oscuro else ft.Icons.DARK_MODE,
                            icon_color="#D32F2F",
                            icon_size=28,
                            tooltip="Cambiar tema Claro/Oscuro",
                            on_click=cambiar_tema,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20,
            )
        ]

        if not datos_paquetes:
            controles.append(
                ft.Container(
                    content=ft.Text("No se pudieron cargar historias desde el archivo local ni desde GitHub.", color="red", size=16),
                    padding=20,
                )
            )

        for paquete in datos_paquetes:
            nombre = paquete.get("nombre", "Sin nombre")
            pkg_id = paquete.get("id_paquete") or nombre
            
            historias_paquete = paquete.get("historias") or paquete.get("stories") or []
            total_historias = len(historias_paquete)
            subtitulo_conteo = f"{total_historias} historias" if total_historias != 1 else "1 historia"
            
            tarjeta = ft.GestureDetector(
                content=ft.Card(
                    elevation=4,
                    content=ft.Container(
                        bgcolor=bg_card,
                        border_radius=10,
                        padding=18,
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.FOLDER_SPECIAL, color="#D32F2F", size=32),
                                ft.Column(
                                    [
                                        ft.Text(nombre, size=20, weight=ft.FontWeight.BOLD, color=texto_principal),
                                        ft.Text(subtitulo_conteo, size=14, color=texto_secundario),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                                ft.Icon(ft.Icons.CHEVRON_RIGHT, color=texto_secundario, size=24),
                            ],
                            spacing=15,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ),
                ),
                on_tap=lambda e, p_id=pkg_id: ir_a(f"/paquete/{p_id}"),
            )
            controles.append(tarjeta)

        # Barra de estado inferior (fija al fondo de la pantalla)
        indicador_icono = (
            ft.ProgressRing(width=12, height=12, stroke_width=2, color="#D32F2F")
            if sincronizando
            else ft.Icon(ft.Icons.WIFI if modo_remoto else ft.Icons.WIFI_OFF, size=14, color="#D32F2F")
        )

        barra_estado = ft.Container(
            content=ft.Row(
                [
                    indicador_icono,
                    ft.Text(estado_sincronizacion, size=12, color=texto_secundario),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            bgcolor=bg_card,
            padding=10,
            border_radius=ft.BorderRadius(top_left=10, top_right=10, bottom_left=0, bottom_right=0),
        )

        return ft.View(
            route="/",
            controls=[
                ft.Column(
                    controls=[
                        ft.ListView(expand=True, spacing=15, padding=20, controls=controles),
                        barra_estado,
                    ],
                    expand=True,
                    spacing=0,
                )
            ],
            bgcolor=bg_color_actual,
        )

    # --- VISTA 2: LISTA DE HISTORIAS ---
    def vista_paquete(pkg_id: str):
        es_oscuro = (page.theme_mode == ft.ThemeMode.DARK)
        bg_card = "#1E1E1E" if es_oscuro else "#FFFFFF"
        texto_principal = "white" if es_oscuro else "black"

        paquete = next((p for p in datos_paquetes if p.get("id_paquete") == pkg_id or p.get("nombre") == pkg_id), None)

        if not paquete:
            return ft.View(
                route=f"/paquete/{pkg_id}",
                controls=[
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=texto_principal, on_click=lambda _: ir_a("/")),
                    ft.Text(f"Colección '{pkg_id}' no encontrada.", color="red", size=18)
                ],
                bgcolor=bg_color_actual,
            )

        stories = paquete.get("historias") or paquete.get("stories") or []

        controles = [
            ft.Container(
                content=ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            icon_color=texto_principal,
                            on_click=lambda _: ir_a("/"),
                        ),
                        ft.Text(
                            paquete.get("nombre", ""),
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color="#D32F2F",
                            text_align=ft.TextAlign.CENTER,
                            expand=True,
                        ),
                        ft.Container(width=48),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=10,
            )
        ]

        if not stories:
            controles.append(
                ft.Container(
                    content=ft.Text(
                        "Esta colección no tiene historias registradas.",
                        color="orange",
                        size=16,
                    ),
                    padding=20,
                )
            )

        stories_ordenadas = sorted(stories, key=lambda x: x.get("id", 0))

        for historia in stories_ordenadas:
            h_id = historia.get("id", 0)
            h_titulo = historia.get("titulo", "Misterio")
            h_imagen = resolver_ruta_imagen(historia.get("imagen", ""))

            tarjeta = ft.Card(
                elevation=4,
                content=ft.Container(
                    bgcolor=bg_card,
                    border_radius=10,
                    padding=12,
                    ink=True,
                    on_click=lambda e, id_h=h_id, p_id=pkg_id: ir_a(f"/juego/{p_id}/{id_h}"),
                    content=ft.Column(
                        [
                            ft.Image(
                                src=h_imagen,
                                height=160,
                                width=None,
                                fit="cover",
                                border_radius=10,
                                error_content=ft.Container(
                                    height=160,
                                    bgcolor="#2A2A2A" if es_oscuro else "#E0E0E0",
                                    alignment=ft.Alignment(0, 0),
                                    border_radius=10,
                                    content=ft.Icon(ft.Icons.BROKEN_IMAGE, color="white54" if es_oscuro else "black38", size=40),
                                ),
                            ),
                            ft.Text(
                                f"#{h_id} - {h_titulo}",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=texto_principal,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                ),
            )
            controles.append(tarjeta)

        return ft.View(
            route=f"/paquete/{pkg_id}",
            controls=[ft.ListView(expand=True, spacing=15, padding=20, controls=controles)],
            bgcolor=bg_color_actual,
        )

    # --- VISTA 3: PANTALLA DE JUEGO ---
    def vista_juego(pkg_id: str, historia_id: int):
        es_oscuro = (page.theme_mode == ft.ThemeMode.DARK)
        bg_card = "#1E1E1E" if es_oscuro else "#FFFFFF"
        texto_principal = "white" if es_oscuro else "black"
        texto_secundario = "white90" if es_oscuro else "black87"
        color_divider = "white24" if es_oscuro else "black12"

        paquete = next((p for p in datos_paquetes if p.get("id_paquete") == pkg_id or p.get("nombre") == pkg_id), None)

        if not paquete:
            return ft.View(route=f"/juego/{pkg_id}/{historia_id}", controls=[ft.Text("Error paquete")], bgcolor=bg_color_actual)

        stories = paquete.get("historias") or paquete.get("stories") or []
        historia = next((h for h in stories if h.get("id") == historia_id), None)

        if not historia:
            return ft.View(route=f"/juego/{pkg_id}/{historia_id}", controls=[ft.Text("Historia no encontrada")], bgcolor=bg_color_actual)

        mostrando_frente = True

        async def girar_tarjeta(e):
            nonlocal mostrando_frente

            tarjeta_contenedor.animate_scale = ft.Animation(180, curve=ft.AnimationCurve.EASE_IN)
            tarjeta_contenedor.scale = ft.Scale(scale_x=0.0, scale_y=1.12)
            page.update()

            await asyncio.sleep(0.18)

            mostrando_frente = not mostrando_frente
            if mostrando_frente:
                tarjeta_contenedor.content = tarjeta_frente_content
                tarjeta_contenedor.border = None
            else:
                tarjeta_contenedor.content = tarjeta_reverso_content
                tarjeta_contenedor.border = ft.Border.all(2, "#D32F2F")

            tarjeta_contenedor.animate_scale = ft.Animation(180, curve=ft.AnimationCurve.EASE_OUT)
            tarjeta_contenedor.scale = ft.Scale(scale_x=1.0, scale_y=1.0)
            page.update()

        tarjeta_frente_content = ft.Column(
            [
                ft.Image(
                    src=resolver_ruta_imagen(historia.get("imagen", "")),
                    height=200,
                    width=None,
                    fit="cover",
                    border_radius=10,
                    error_content=ft.Container(
                        height=200,
                        bgcolor="#2A2A2A" if es_oscuro else "#E0E0E0",
                        alignment=ft.Alignment(0, 0),
                        border_radius=10,
                        content=ft.Icon(ft.Icons.IMAGE, color="white54" if es_oscuro else "black38", size=50),
                    ),
                ),
                ft.Text(
                    historia.get("titulo", ""),
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=texto_principal,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Divider(color=color_divider),
                ft.Text(
                    historia.get("descripcion", ""),
                    size=17,
                    color=texto_secundario,
                    text_align=ft.TextAlign.JUSTIFY,
                ),
                ft.Divider(color=color_divider),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.KEY, color="white", size=20),
                            ft.Text("Ver Solución", color="white", weight=ft.FontWeight.BOLD),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    bgcolor="#B71C1C",
                    padding=12,
                    border_radius=8,
                    ink=True,
                    on_click=girar_tarjeta,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
        )

        tarjeta_reverso_content = ft.Column(
            [
                ft.Icon(ft.Icons.KEY_OFF, color="#D32F2F", size=48),
                ft.Text(
                    "SOLUCIÓN",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color="#D32F2F",
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Divider(color=color_divider),
                ft.Text(
                    historia.get("solucion", ""),
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color="#EF5350" if es_oscuro else "#C62828",
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Divider(color=color_divider),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.REPLAY, color="white", size=20),
                            ft.Text("Volver a la Historia", color="white", weight=ft.FontWeight.BOLD),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    bgcolor="#333333" if es_oscuro else "#616161",
                    padding=12,
                    border_radius=8,
                    ink=True,
                    on_click=girar_tarjeta,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
        )

        tarjeta_contenedor = ft.Container(
            padding=18,
            bgcolor=bg_card,
            border_radius=15,
            border=None,
            content=tarjeta_frente_content,
            scale=ft.Scale(scale_x=1.0, scale_y=1.0),
            animate_scale=ft.Animation(180, curve=ft.AnimationCurve.EASE_IN),
        )

        contenido_juego = [
            ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_color=texto_principal,
                        on_click=lambda _: ir_a(f"/paquete/{pkg_id}"),
                    ),
                    ft.Text(
                        f"Misterio #{historia.get('id')}",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color="#D32F2F",
                        text_align=ft.TextAlign.CENTER,
                        expand=True,
                    ),
                    ft.Container(width=48),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            tarjeta_contenedor,
        ]

        return ft.View(
            route=f"/juego/{pkg_id}/{historia_id}",
            controls=[ft.ListView(expand=True, spacing=15, padding=20, controls=contenido_juego)],
            bgcolor=bg_color_actual,
        )

    # --- ROUTER DE RUTAS ---
    def route_change(e):
        page.views.clear()

        page.views.append(vista_colecciones())

        ruta_actual = page.route or "/"

        if ruta_actual.startswith("/paquete/"):
            pkg_id = ruta_actual.split("/paquete/", 1)[1]
            page.views.append(vista_paquete(pkg_id))

        elif ruta_actual.startswith("/juego/"):
            partes = ruta_actual.split("/juego/", 1)[1].split("/")
            if len(partes) == 2:
                pkg_id = partes[0]
                try:
                    historia_id = int(partes[1])
                    page.views.append(vista_paquete(pkg_id))
                    page.views.append(vista_juego(pkg_id, historia_id))
                except ValueError:
                    pass

        page.update()

    def view_pop(e: ft.ViewPopEvent):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.route = top_view.route
            page.update()

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    ir_a(page.route or "/")

if __name__ == "__main__":
    run(main, assets_dir="assets")