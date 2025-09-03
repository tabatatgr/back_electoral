#!/usr/bin/env python3
"""
Validador de configuraciones electorales
Verifica la coherencia lógica de los parámetros antes del procesamiento
"""

def validar_configuracion_electoral(sistema, max_seats, mr_seats=None, rp_seats=None, pm_seats=None):
    """
    Valida que la configuración electoral sea lógicamente coherente
    
    Args:
        sistema: "mr" o "mixto"
        max_seats: Total de escaños
        mr_seats: Escaños de mayoría relativa (solo mixto)
        rp_seats: Escaños de representación proporcional (solo mixto)
        pm_seats: Escaños de primera minoría
    
    Returns:
        dict: {"valid": bool, "errors": list, "warnings": list}
    """
    
    errors = []
    warnings = []
    
    # 📊 VALIDACIONES BÁSICAS
    if max_seats <= 0:
        errors.append(f"❌ Total de escaños debe ser positivo (recibido: {max_seats})")
    
    if max_seats > 1000:
        warnings.append(f"⚠️ Total de escaños muy alto ({max_seats}), ¿es correcto?")
    
    # 🏛️ VALIDACIONES ESPECÍFICAS POR SISTEMA
    if sistema == "mr":
        # Sistema MR Puro
        if mr_seats is not None and mr_seats != max_seats:
            warnings.append(f"⚠️ En MR puro, mr_seats debería ser igual a max_seats")
        
        if rp_seats is not None and rp_seats > 0:
            errors.append(f"❌ Sistema MR puro no debe tener escaños RP (recibido: {rp_seats})")
        
        # Validar PM en MR puro
        if pm_seats is not None:
            if pm_seats > max_seats:
                errors.append(f"❌ PM ({pm_seats}) no puede ser mayor que total MR ({max_seats})")
            elif pm_seats < 0:
                errors.append(f"❌ PM no puede ser negativo (recibido: {pm_seats})")
            elif pm_seats == max_seats:
                warnings.append(f"⚠️ PM igual a total ({pm_seats}) = 100% segunda fuerza")
    
    elif sistema == "mixto":
        # Sistema Mixto
        if mr_seats is None or rp_seats is None:
            errors.append(f"❌ Sistema mixto requiere mr_seats y rp_seats definidos")
        else:
            # Validar suma MR + RP
            suma_mr_rp = mr_seats + rp_seats
            if suma_mr_rp != max_seats:
                errors.append(f"❌ MR ({mr_seats}) + RP ({rp_seats}) = {suma_mr_rp} ≠ Total ({max_seats})")
            
            # Validar valores individuales
            if mr_seats <= 0:
                errors.append(f"❌ Escaños MR debe ser positivo (recibido: {mr_seats})")
            if rp_seats <= 0:
                errors.append(f"❌ Escaños RP debe ser positivo (recibido: {rp_seats})")
            
            # Validar PM en sistema mixto
            if pm_seats is not None:
                if pm_seats > mr_seats:
                    errors.append(f"❌ PM ({pm_seats}) no puede ser mayor que MR ({mr_seats})")
                elif pm_seats < 0:
                    errors.append(f"❌ PM no puede ser negativo (recibido: {pm_seats})")
                elif pm_seats == mr_seats:
                    warnings.append(f"⚠️ PM igual a MR ({pm_seats}) = 100% segunda fuerza en MR")
            
            # Advertencias sobre proporciones
            if mr_seats > max_seats * 0.8:
                warnings.append(f"⚠️ MR muy alto ({mr_seats}/{max_seats} = {mr_seats/max_seats:.1%})")
            if rp_seats > max_seats * 0.8:
                warnings.append(f"⚠️ RP muy alto ({rp_seats}/{max_seats} = {rp_seats/max_seats:.1%})")
    
    else:
        errors.append(f"❌ Sistema desconocido: {sistema} (debe ser 'mr' o 'mixto')")
    
    # 🔢 VALIDACIONES DE CONFIGURACIONES COMUNES
    if max_seats % 2 != 0:
        warnings.append(f"⚠️ Total de escaños impar ({max_seats}) puede causar problemas de empate")
    
    # Configuraciones típicas
    if max_seats == 128 and sistema == "mixto":
        if mr_seats == 96 and rp_seats == 32:
            warnings.append(f"✅ Configuración actual del Senado mexicano")
    elif max_seats == 96 and sistema == "mixto":
        if mr_seats == 64 and rp_seats == 32:
            warnings.append(f"✅ Configuración común de prueba")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "sistema": sistema,
            "total": max_seats,
            "mr": mr_seats,
            "rp": rp_seats,
            "pm": pm_seats,
            "mr_efectivo": mr_seats - (pm_seats or 0) if mr_seats and pm_seats else None
        }
    }

def mostrar_validacion(validacion):
    """
    Muestra los resultados de la validación de forma legible
    """
    print(f"🔍 VALIDACIÓN DE CONFIGURACIÓN")
    print("=" * 40)
    
    summary = validacion["summary"]
    print(f"📊 Sistema: {summary['sistema'].upper()}")
    print(f"📈 Total escaños: {summary['total']}")
    
    if summary['mr'] is not None:
        print(f"🏛️ MR: {summary['mr']}")
    if summary['rp'] is not None:
        print(f"📊 RP: {summary['rp']}")
    if summary['pm'] is not None:
        print(f"🔥 PM: {summary['pm']}")
        if summary['mr_efectivo'] is not None:
            print(f"⚖️ MR efectivo: {summary['mr_efectivo']}")
    
    print()
    
    # Mostrar errores
    if validacion["errors"]:
        print("🚨 ERRORES:")
        for error in validacion["errors"]:
            print(f"   {error}")
        print()
    
    # Mostrar advertencias
    if validacion["warnings"]:
        print("⚠️ ADVERTENCIAS:")
        for warning in validacion["warnings"]:
            print(f"   {warning}")
        print()
    
    # Resultado final
    if validacion["valid"]:
        print("✅ CONFIGURACIÓN VÁLIDA")
    else:
        print("❌ CONFIGURACIÓN INVÁLIDA")
    
    print("=" * 40)
    return validacion["valid"]

# 🧪 EJEMPLOS DE USO
if __name__ == "__main__":
    print("🧪 PROBANDO VALIDADOR DE CONFIGURACIONES")
    print()
    
    # Casos de prueba
    test_cases = [
        {
            "nombre": "✅ Senado actual",
            "params": {"sistema": "mixto", "max_seats": 128, "mr_seats": 96, "rp_seats": 32, "pm_seats": 32}
        },
        {
            "nombre": "✅ Configuración personalizada 200 escaños",
            "params": {"sistema": "mixto", "max_seats": 200, "mr_seats": 120, "rp_seats": 80, "pm_seats": 60}
        },
        {
            "nombre": "❌ PM mayor que MR",
            "params": {"sistema": "mixto", "max_seats": 100, "mr_seats": 60, "rp_seats": 40, "pm_seats": 70}
        },
        {
            "nombre": "❌ MR + RP ≠ Total",
            "params": {"sistema": "mixto", "max_seats": 100, "mr_seats": 60, "rp_seats": 50, "pm_seats": 20}
        },
        {
            "nombre": "✅ MR puro con PM",
            "params": {"sistema": "mr", "max_seats": 64, "pm_seats": 16}
        },
        {
            "nombre": "❌ PM mayor que total MR",
            "params": {"sistema": "mr", "max_seats": 64, "pm_seats": 80}
        }
    ]
    
    for test_case in test_cases:
        print(f"🔬 {test_case['nombre']}")
        validacion = validar_configuracion_electoral(**test_case['params'])
        mostrar_validacion(validacion)
        print()
