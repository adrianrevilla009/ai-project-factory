# Estándares · 12-aws-networking

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## alb-nlb-and-tls-termination

- **MUST** elegir ALB para HTTP/HTTPS/gRPC (rutas, host, WAF) y NLB para TCP/TLS, IP estática o PrivateLink.
- **MUST** servir solo HTTPS en listeners públicos; el puerto 80 solo redirige a 443 (HTTP 301).
- **MUST** usar certificados de ACM (renovación automática) por región; para CloudFront el certificado vive en us-east-1.
- **MUST** fijar una política TLS moderna (TLS 1.2 mínimo, preferible 1.3) con una `ssl_policy` explícita, no la heredada por defecto (TODO-VERIFY nombre vigente).
- **MUST** activar `drop_invalid_header_fields`, access logs a S3 y `enable_deletion_protection` en producción.
- **MUST NOT** terminar TLS en el balanceador y reenviar HTTP en claro hacia pods con datos sensibles: recifrar hacia el backend (HTTPS al target o mTLS de malla).
- **SHOULD** usar `target-type: ip` con AWS Load Balancer Controller en EKS (ver `eks-networking`) y health checks dedicados.
- **SHOULD** un balanceador interno por frontera de confianza; SG del balanceador como único origen permitido en los SG de cómputo.

## cidr-planning-and-ipam

- **MUST** asignar los CIDR desde un plan central único (fichero versionado o AWS IPAM), nunca a mano por equipo.
- **MUST NOT** solapar CIDR entre VPCs, regiones, cuentas ni con on-premises: un solapamiento no se arregla después sin recrear la VPC.
- **MUST** reservar bloques por región (eu-west-1 primaria, eu-central-1 secundaria, D6) y por entorno, dejando hueco de crecimiento (>= 50 % libre).
- **MUST** dimensionar VPC en /16 (workloads) y subredes /20 (privadas) o /24 (públicas, datos pequeños); AWS reserva 5 direcciones por subred.
- **SHOULD** usar `aws_vpc_ipam` con pools por región y `ipv4_ipam_pool_id` en `aws_vpc`, de modo que el solapamiento sea imposible por construcción.
- **SHOULD** dar a EKS un CIDR secundario dedicado a pods (p. ej. rango 100.64.0.0/10, ver `eks-networking`) para no agotar IPs.
- **MUST NOT** usar la VPC por defecto ni rangos 172.31.0.0/16 de la VPC por defecto.
- **MUST** documentar el plan en una tabla (región, entorno, CIDR, propietario, estado).

## dns-route53-private-and-hybrid

- **MUST** usar un esquema de nombres por entorno y región (p. ej. `orders.prod.euw1.internal.example.com`) y no reutilizar el mismo nombre privado con IP distinta entre regiones.
- **MUST** crear zonas privadas en la cuenta de red y asociarlas a las VPC consumidoras (`aws_route53_vpc_association_authorization` + `aws_route53_zone_association` entre cuentas).
- **MUST** tener `enable_dns_support` y `enable_dns_hostnames` activos en las VPC con zonas privadas o endpoints.
- **MUST** desplegar Resolver endpoints con al menos 2 IP en AZ distintas: inbound (on-prem hacia AWS) y outbound (AWS hacia on-prem con reglas por dominio).
- **MUST NOT** hacer forwarding recursivo de todo (`.`) a on-premises; solo dominios corporativos concretos.
- **SHOULD** activar DNSSEC en zonas públicas y query logging de Resolver/zonas hacia el archivo de logs (ver `flow-logs-and-network-observability`).
- **SHOULD** usar TTL bajos (<= 60 s) solo en registros de failover; el resto con TTL moderado.
- **SHOULD** gestionar los registros de los balanceadores como alias, no CNAME, en el ápice.

## private-endpoints-and-egress-control

- **MUST** crear gateway endpoints para S3 (y DynamoDB si se usa): no tienen coste por hora y sacan el tráfico del NAT.
- **MUST** crear interface endpoints para los servicios que usa EKS/CI (ECR api y dkr, STS, Logs, KMS, Secrets Manager) y activar `private_dns_enabled`.
- **MUST** adjuntar una política de endpoint que limite a principals y recursos de la organización (condición `aws:PrincipalOrgID`), no `"*"`.
- **MUST** poner interface endpoints en subredes de todas las AZ y un SG que solo acepte 443 desde los SG de cómputo.
- **MUST** tratar el egress como denegado por defecto: lo que sale a Internet pasa por NAT o un punto central con allowlist de dominios (AWS Network Firewall u otro proxy con FQDN).
- **MUST NOT** dar IP pública a cargas para que "salgan"; ni abrir egress 0.0.0.0/0 en SG de datos.
- **SHOULD** compartir endpoints en una VPC de servicios solo si el ahorro compensa el coste de TGW y la complejidad de DNS (ver `dns-route53-private-and-hybrid`).
- **SHOULD** medir coste: cada interface endpoint cobra por hora y AZ y por GB (TODO-VERIFY tarifas vigentes).

## transit-gateway-hub-and-spoke

- **MUST** crear un TGW por región (eu-west-1 y eu-central-1, D6) en la cuenta de red y compartirlo con RAM; los spokes solo crean attachments.
- **MUST** desactivar asociación y propagación por defecto (`default_route_table_association/propagation = "disable"`) y gestionar tablas explícitas (spokes, shared, inspección).
- **MUST** segmentar: las VPC de entornos distintos (dev/prod) no deben tener ruta entre sí; la ausencia de ruta es el control.
- **MUST** activar `appliance_mode_support = "enable"` en el attachment de la VPC de inspección para mantener simetría por AZ.
- **MUST** usar rutas estáticas en el peering inter-región (no hay propagación dinámica) y registrarlas en código.
- **MUST NOT** usar rutas 0.0.0.0/0 en spokes hacia el TGW sin pasar por inspección/egress controlado (ver `private-endpoints-and-egress-control`).
- **SHOULD** usar un attachment por AZ con subredes /28 dedicadas de TGW.
- **SHOULD** evitar TGW si el tráfico entre VPC es masivo y el coste por GB lo desaconseja (ver `cross-region-connectivity-and-cost`).

## vpc-multi-az-layers

- **MUST** usar como mínimo 3 AZ por VPC (o 2 si la región lo limita) y la misma estructura de capas en cada una.
- **MUST** separar tres capas de subredes: pública (solo balanceadores y NAT), privada (cómputo/EKS) y datos (bases, caches), cada una con su route table.
- **MUST NOT** asignar IP pública por defecto a subredes (`map_public_ip_on_launch = false`) ni colocar cómputo o datos en subredes públicas.
- **MUST** poner un NAT Gateway por AZ y rutear cada subred privada al NAT de su propia AZ (evita tráfico y fallo cross-AZ).
- **MUST** restringir el security group por defecto (`aws_default_security_group` sin reglas) y usar SG por rol, referenciando otros SG como origen en vez de CIDR.
- **MUST NOT** abrir 0.0.0.0/0 en ingress salvo 443 hacia el balanceador público; sin SSH/RDP abierto (usar SSM Session Manager).
- **SHOULD** usar NACL solo como red de seguridad gruesa (denegar rangos conocidos); la lógica fina va en SG.
- **SHOULD** activar `enable_dns_support` y `enable_dns_hostnames` (requisito de endpoints y zonas privadas).
- **SHOULD** etiquetar subredes con rol y entorno (ver `tagging-cost-allocation-budgets`).
