import os

def stitch_report():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Read the base template
    with open(os.path.join(base_dir, '00_template_base.html'), 'r', encoding='utf-8') as f:
        template = f.read()
        
    # 2. Collect all the html fragments sequentially
    fragments = [
        '01_portada.html',
        '02_introduccion.html',
        '03_modelo_evaluacion.html',
        '04_perfil_poblacion.html',
        '06_perfil_demografico.html',
        '07_portada_intralaboral.html',
        '08_dimensiones_descripcion.html',
        '09_resultado_general_intra.html',
        '10_resultados_por_area.html',
        '11_portada_liderazgo.html',
        '12_resultados_liderazgo.html',
        '13_liderazgo_foco_areas.html',
        '14_liderazgo_foco_areas_2.html',
        '15_liderazgo_comparativa_formas.html',
        '15_portada_demandas.html',
        '16_resultado_general_demandas.html',
        '17_resultados_demandas.html',
        '18_demandas_por_area.html',
        '19_demandas_comparativa_formas.html',
        '21_portada_control.html',
        '22_resultado_general_control.html',
        '23_resultados_control.html',
        '24_portada_recompensas.html',
        '25_resultado_general_recompensas.html',
        '26_resultados_recompensas.html'
    ]
    
    content_html = ""
    for frag in fragments:
        frag_path = os.path.join(base_dir, frag)
        if os.path.exists(frag_path):
            with open(frag_path, 'r', encoding='utf-8') as f:
                content_html += f.read() + "\n"
                
    # 3. Inject the fragments into the placeholder
    final_html = template.replace('<!-- CONTENT_PLACEHOLDER -->', content_html)
    
    # 4. Save to the main frontend output directory
    output_path = os.path.join(os.path.dirname(base_dir), 'reporte-grupal-total.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
        
    print(f"Report stitched successfully! Saved to: {output_path}")

if __name__ == "__main__":
    stitch_report()
