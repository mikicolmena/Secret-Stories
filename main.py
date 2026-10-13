import json
import flet as ft
from flet.app import run

def main(page: ft.Page):
    page.title = "Secret Stories"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    # Variable local para rastrear el color de fondo de la app
    bg_color_actual = "#121212"
    page.bgcolor = bg_color_actual

    # Normalizar ruta de imagen por si empieza por "assets/"
    def limpiar_ruta_imagen(ruta: str) -> str:
        if not ruta:
            return ""
        if ruta.startswith("assets/"):
            return ruta.replace("assets/", "", 1)
        return ruta

    # --- FUNCIÓN DE NAVEGACIÓN COMPATIBLE CON FLET 1.0 ---
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

    # --- CARGA SEGURA DE DATOS ---
    datos_paquetes = []
    try:
        with open("stories.json", "r", encoding="utf-8") as f:
            content = json.load(f)
            datos_paquetes = content.get("paquetes", [])
            print(f"-> 'stories.json' cargado con éxito. Colecciones encontradas: {len(datos_paquetes)}")
    except FileNotFoundError:
        print("Aviso: No se encontró stories.json en la carpeta actual.")
    except json.JSONDecodeError:
        print("Error: stories.json no tiene un formato JSON válido.")

    # --- VISTA 1: MENÚ DE COLECCIONES (PANTALLA PRINCIPAL) ---
    def vista_colecciones():
        es_oscuro = (page.theme_mode == ft.ThemeMode.DARK)
        bg_card = "#1E1E1E" if es_oscuro else "#FFFFFF"
        texto_principal = "white" if es_oscuro else "black"
        texto_secundario = "white70" if es_oscuro else "black54"

        controles = [
            ft.Container(
                content=ft.Row(
                    [
                        # Espaciador invisible para mantener centrado el título
                        ft.Container(width=48),
                        ft.Column(
                            [
                                ft.Text("Secret Stories", size=32, weight=ft.FontWeight.BOLD, color="#D32F2F", text_align=ft.TextAlign.CENTER),
                                ft.Text("Selecciona una Colección", size=16, color=texto_secundario, text_align=ft.TextAlign.CENTER),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        # Botón para cambiar tema Claro / Oscuro a la derecha
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
                    content=ft.Text("Crea o revisa 'stories.json' para cargar colecciones.", color="red", size=16),
                    padding=20,
                )
            )

        for paquete in datos_paquetes:
            nombre = paquete.get("nombre", "Sin nombre")
            pkg_id = paquete.get("id_paquete") or nombre
            
            tarjeta = ft.GestureDetector(
                content=ft.Card(
                    elevation=4,
                    content=ft.Container(
                        bgcolor=bg_card,
                        border_radius=10,
                        padding=20,
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.FOLDER_SPECIAL, color="#D32F2F", size=28),
                                ft.Text(nombre, size=20, weight=ft.FontWeight.BOLD, color=texto_principal),
                            ],
                            spacing=15,
                        ),
                    ),
                ),
                on_tap=lambda e, p_id=pkg_id: ir_a(f"/paquete/{p_id}"),
            )
            controles.append(tarjeta)

        return ft.View(
            route="/",
            controls=[ft.ListView(expand=True, spacing=15, padding=20, controls=controles)],
            bgcolor=bg_color_actual,
        )

    # --- VISTA 2: LISTA DE HISTORIAS DE UN PAQUETE ---
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
            h_imagen = limpiar_ruta_imagen(historia.get("imagen", ""))

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

    # --- VISTA 3: PANTALLA DE JUEGO (MISTERIO & SOLUCIÓN CON GIRO DE TARJETA) ---
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

        # Función de giro para la animación
        def girar_tarjeta(e):
            if tarjeta_animada.content.key == "frente":
                tarjeta_animada.content = tarjeta_reverso
            else:
                tarjeta_animada.content = tarjeta_frente
            page.update()

        # --- CARA FRONTAL: HISTORIA ---
        tarjeta_frente = ft.Container(
            key="frente",
            padding=15,
            bgcolor=bg_card,
            border_radius=15,
            content=ft.Column(
                [
                    ft.Image(
                        src=limpiar_ruta_imagen(historia.get("imagen", "")),
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
            ),
        )

        # --- CARA TRASERA: SOLUCIÓN ---
        tarjeta_reverso = ft.Container(
            key="reverso",
            padding=20,
            bgcolor=bg_card,
            border_radius=15,
            border=ft.Border.all(2, "#D32F2F"),  # <--- CORREGIDO: ft.Border.all
            content=ft.Column(
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
            ),
        )

        # Contenedor animado para la transición al girar de cara
        tarjeta_animada = ft.AnimatedSwitcher(
            content=tarjeta_frente,
            duration=400,
            reverse_duration=400,
            switch_in_curve="easeOutBack",
            switch_out_curve="easeInBack",
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
            tarjeta_animada,
        ]

        return ft.View(
            route=f"/juego/{pkg_id}/{historia_id}",
            controls=[ft.ListView(expand=True, spacing=15, padding=20, controls=contenido_juego)],
            bgcolor=bg_color_actual,
        )

    # --- ROUTER DE RUTAS ---
    def route_change(e):
        page.views.clear()

        # Vista Raíz
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