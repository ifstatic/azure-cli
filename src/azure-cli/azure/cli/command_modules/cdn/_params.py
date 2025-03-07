# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.arguments import CLIArgumentType

from azure.mgmt.cdn.models import (QueryStringCachingBehavior, SkuName, ActionType, EnabledState, HttpsRedirect,
                                   HealthProbeRequestType, ProbeProtocol, MatchProcessingBehavior, DeliveryRuleAction,
                                   AFDEndpointProtocols, ForwardingProtocol, LinkToDefaultDomain, DeliveryRuleCondition,
                                   AfdCertificateType, AfdMinimumTlsVersion)

from azure.cli.core.commands.parameters import get_three_state_flag, tags_type, get_enum_type
from azure.cli.core.commands.validators import get_default_location_from_resource_group

from ._validators import (validate_origin, validate_priority)
from ._actions import (OriginType, MatchConditionAction, ManagedRuleOverrideAction)


# pylint:disable=too-many-statements
def load_arguments(self, _):

    name_arg_type = CLIArgumentType(options_list=('--name', '-n'), metavar='NAME')
    endpoint_name_type = CLIArgumentType(options_list=('--endpoint-name'), metavar='ENDPOINT_NAME')
    origin_group_name_type = CLIArgumentType(options_list=('--origin-group-name'), metavar='ORIGIN_GROUP_NAME')
    rule_set_name_type = CLIArgumentType(options_list=('--rule-set-name'), metavar='RULE_SET_NAME')
    route_name_type = CLIArgumentType(options_list=('--route-name'), metavar='ROUTE_NAME')
    rule_name_type = CLIArgumentType(options_list=('--rule-name'), metavar='RULE_NAME')
    custom_name_arg_type = CLIArgumentType(options_list=('--custom-domain-name'), metavar='CUSTOM_DOMAIN_NAME')
    secret_name_arg_type = CLIArgumentType(options_list=('--secret-name'), metavar='SECRET_NAME')
    origin_name_type = CLIArgumentType(options_list=('--origin-name'), metavar='ORIGIN_NAME')
    profile_name_help = 'Name of the CDN profile which is unique within the resource group.'

    with self.argument_context('cdn') as c:
        c.argument('name', name_arg_type, id_part='name')
        c.argument('tags', tags_type)

    # Profile #
    with self.argument_context('cdn profile') as c:
        c.argument('profile_name', name_arg_type, id_part='name', help=profile_name_help)

    with self.argument_context('cdn profile create') as c:
        # Remove Stardard/Premium Front Door from old cdn profile's supported SKU list
        supported_skus = [item.value for item in list(SkuName) if item.value not in
                          (SkuName.premium_azure_front_door, SkuName.standard_azure_front_door)]
        c.argument('sku', arg_type=get_enum_type(supported_skus))
        c.argument('location', validator=get_default_location_from_resource_group)
        c.argument('name', name_arg_type, id_part='name', help=profile_name_help)

    # Endpoint #

    with self.argument_context('cdn endpoint') as c:
        c.argument('content_paths', nargs='+')
        c.argument('endpoint_name', name_arg_type, id_part='child_name_1', help='Name of the CDN endpoint.')
        c.argument('location', validator=get_default_location_from_resource_group)
        c.argument('origins', options_list='--origin', nargs='+', action=OriginType, validator=validate_origin,
                   help='Endpoint origin specified by the following space-delimited 6 tuple: '
                        '`www.example.com http_port https_port private_link_resource_id private_link_location '
                        'private_link_approval_message`. The HTTP and HTTPS ports and the private link resource ID and '
                        'location are optional. The HTTP and HTTPS ports default to 80 and 443, respectively. Private '
                        'link fields are only valid for the sku Standard_Microsoft, and private_link_location is '
                        'required if private_link_resource_id is set.')
        c.argument('is_http_allowed', arg_type=get_three_state_flag(invert=True), options_list='--no-http',
                   help='Indicates whether HTTP traffic is not allowed on the endpoint. '
                   'Default is to allow HTTP traffic.')
        c.argument('is_https_allowed', arg_type=get_three_state_flag(invert=True), options_list='--no-https',
                   help='Indicates whether HTTPS traffic is not allowed on the endpoint. '
                   'Default is to allow HTTPS traffic.')
        c.argument('is_compression_enabled', arg_type=get_three_state_flag(), options_list='--enable-compression',
                   help='If compression is enabled, content will be served as compressed if '
                        'user requests for a compressed version. Content won\'t be compressed '
                        'on CDN when requested content is smaller than 1 byte or larger than 1 '
                        'MB.')
        c.argument('profile_name', help=profile_name_help, id_part='name')

    with self.argument_context('cdn endpoint update') as c:
        caching_behavior = [item.value for item in list(QueryStringCachingBehavior)]
        c.argument('query_string_caching_behavior', options_list='--query-string-caching',
                   arg_type=get_enum_type(caching_behavior))
        c.argument('content_types_to_compress', nargs='+')

    with self.argument_context('cdn endpoint rule') as c:
        configure_rule_parameters(c)

    with self.argument_context('cdn endpoint create') as c:
        c.argument('name', name_arg_type, id_part='name', help='Name of the CDN endpoint.')
    with self.argument_context('cdn endpoint set') as c:
        c.argument('name', name_arg_type, id_part='name', help='Name of the CDN endpoint.')

    with self.argument_context('cdn endpoint list') as c:
        c.argument('profile_name', id_part=None)

    with self.argument_context('cdn endpoint waf') as c:
        c.argument('endpoint_name', endpoint_name_type, help='Name of the CDN endpoint.')

    # Custom Domain #

    with self.argument_context('cdn custom-domain') as c:
        c.argument('custom_domain_name', name_arg_type, id_part=None, help='Resource name of the custom domain.')

    with self.argument_context('cdn custom-domain create') as c:
        c.argument('location', validator=get_default_location_from_resource_group)

    with self.argument_context('cdn custom-domain enable-https') as c:
        c.argument('profile_name', id_part=None, help='Name of the parent profile.')
        c.argument('endpoint_name', help='Name of the parent endpoint.')
        c.argument('custom_domain_name', name_arg_type, help='Resource name of the custom domain.')
        c.argument('min_tls_version',
                   help='The minimum TLS version required for the custom domain.',
                   arg_type=get_enum_type(['none', '1.0', '1.2']))
        c.argument('user_cert_protocol_type',
                   arg_group='Bring Your Own Certificate',
                   help='The protocol type of the certificate.',
                   arg_type=get_enum_type(['sni', 'ip']))
        c.argument('user_cert_subscription_id',
                   arg_group='Bring Your Own Certificate',
                   help='The subscription id of the KeyVault certificate')
        c.argument('user_cert_group_name',
                   arg_group='Bring Your Own Certificate',
                   help='The resource group of the KeyVault certificate')
        c.argument('user_cert_vault_name',
                   arg_group='Bring Your Own Certificate',
                   help='The vault name of the KeyVault certificate')
        c.argument('user_cert_secret_name',
                   arg_group='Bring Your Own Certificate',
                   help='The secret name of the KeyVault certificate')
        c.argument('user_cert_secret_version',
                   arg_group='Bring Your Own Certificate',
                   help='The secret version of the KeyVault certificate, If not specified, the "Latest" version will '
                        'always been used and the deployed certificate will be automatically rotated to the latest '
                        'version when a newer version of the certificate is available.')

    # Origin #
    with self.argument_context('cdn origin') as c:
        # Some command handlers use name, others origin_name, so we specify both
        c.argument('name', name_arg_type, id_part='child_name_2', help='Name of the origin.')
        c.argument('origin_name', name_arg_type, id_part='child_name_2', help='Name of the origin.')
        c.argument('profile_name', help=profile_name_help, id_part='name')
        c.argument('endpoint_name', endpoint_name_type, id_part='child_name_1', help='Name of the CDN endpoint.')
        c.argument('http_port', type=int)
        c.argument('https_port', type=int)
        c.argument('disabled', arg_type=get_three_state_flag())
        c.argument('priority', type=int)
        c.argument('weight', type=int)
        c.argument('private_link_approval_message', options_list=['--private-link-approval-message', '-m'])
        c.argument('private_link_resource_id', options_list=['--private-link-resource-id', '-p'])
        c.argument('private_link_location', options_list=['--private-link-location', '-l'])
    with self.argument_context('cdn origin list') as c:
        # list commands can't use --ids argument.
        c.argument('profile_name', id_part=None)
        c.argument('endpoint_name', id_part=None)

    with self.argument_context('cdn origin-group') as c:
        # Some command handlers use name, others origin_name, so we specify both
        c.argument('name', name_arg_type, id_part='child_name_2', help='Name of the origin group.')
        c.argument('origin_group_name', name_arg_type, id_part='child_name_2', help='Name of the origin group.')
        c.argument('profile_name', help=profile_name_help, id_part='name')
        c.argument('endpoint_name', endpoint_name_type, id_part='child_name_1', help='Name of the CDN endpoint.')
        c.argument('disabled', arg_type=get_three_state_flag())
        c.argument('probe_method', arg_type=get_enum_type(["HEAD", "GET"]))
        c.argument('probe_protocol', arg_type=get_enum_type(["HTTP", "HTTPS"]))
        c.argument('probe_interval', type=int)
        c.argument('failover_threshold', type=int)
        c.argument('detection_type', arg_type=get_enum_type(["TcpErrorsOnly", "TcpAndHttpErrors"]))

    with self.argument_context('cdn origin-group list') as c:
        # list commands can't use --ids argument.
        c.argument('profile_name', id_part=None)
        c.argument('endpoint_name', id_part=None)

    # WAF #

    with self.argument_context('cdn waf policy set') as c:
        c.argument('disabled', arg_type=get_three_state_flag())
        c.argument('block_response_status_code', type=int)
        c.argument('name', name_arg_type, id_part='name', help='The name of the CDN WAF policy.')
    with self.argument_context('cdn waf policy show') as c:
        c.argument('policy_name', name_arg_type, id_part='name', help='The name of the CDN WAF policy.')
    with self.argument_context('cdn waf policy delete') as c:
        c.argument('policy_name', name_arg_type, id_part='name', help='The name of the CDN WAF policy.')
    with self.argument_context('cdn waf policy set') as c:
        c.argument('waf_policy_resource_group_name', options_list=['--waf-policy-resource-group-name',
                                                                   '--policy-group'])

    with self.argument_context('cdn waf policy managed-rule-set') as c:
        c.argument('policy_name', id_part='name', help='Name of the CDN WAF policy.')
        c.argument('rule_set_type', help='The type of the managed rule set.')
        c.argument('rule_set_version', help='The version of the managed rule set.')
    with self.argument_context('cdn waf policy managed-rule-set list') as c:
        # List commands cannot use --ids flag
        c.argument('policy_name', id_part=None)
    with self.argument_context('cdn waf policy managed-rule-set add') as c:
        c.argument('enabled', arg_type=get_three_state_flag())

    with self.argument_context('cdn waf policy managed-rule-set rule-group-override') as c:
        c.argument('name', name_arg_type, id_part=None, help='The name of the rule group.')
    with self.argument_context('cdn waf policy managed-rule-set rule-group-override list') as c:
        # List commands cannot use --ids flag
        c.argument('policy_name', id_part=None)
    with self.argument_context('cdn waf policy managed-rule-set rule-group-override set') as c:
        c.argument('rule_overrides',
                   options_list=['-r', '--rule-override'],
                   action=ManagedRuleOverrideAction,
                   nargs='+')

    with self.argument_context('cdn waf policy custom-rule') as c:
        c.argument('name', name_arg_type, id_part=None, help='The name of the custom rule.')
        c.argument('policy_name', id_part='name', help='Name of the CDN WAF policy.')
    with self.argument_context('cdn waf policy custom-rule list') as c:
        # List commands cannot use --ids flag
        c.argument('policy_name', id_part=None)
    with self.argument_context('cdn waf policy rate-limit-rule') as c:
        c.argument('name', name_arg_type, id_part=None, help='The name of the rate limit rule.')
        c.argument('policy_name', id_part='name', help='Name of the CDN WAF policy.')
    with self.argument_context('cdn waf policy rate-limit-rule list') as c:
        # List commands cannot use --ids flag
        c.argument('policy_name', id_part=None)

    with self.argument_context('cdn waf policy custom-rule set') as c:
        c.argument('match_conditions', options_list=['-m', '--match-condition'], action=MatchConditionAction, nargs='+')
        c.argument('priority', type=int, validator=validate_priority)
        c.argument('action', arg_type=get_enum_type([item.value for item in list(ActionType)]))

    with self.argument_context('cdn waf policy rate-limit-rule set') as c:
        c.argument('match_conditions', options_list=['-m', '--match-condition'], action=MatchConditionAction, nargs='+')
        c.argument('priority', type=int, validator=validate_priority)
        c.argument('action', arg_type=get_enum_type([item.value for item in list(ActionType)]))
        c.argument('request_threshold', type=int)
        c.argument('duration', type=int)

    # AFDX
    with self.argument_context('afd') as c:
        c.argument('tags', tags_type)

    # AFD Profiles
    with self.argument_context('afd profile') as c:
        c.argument('sku',
                   arg_type=get_enum_type([SkuName.standard_azure_front_door, SkuName.premium_azure_front_door]),
                   help="The pricing tier of the AFD profile.")
        c.argument('profile_name', help=profile_name_help, id_part='name')

    # AFD endpoint #
    with self.argument_context('afd endpoint') as c:
        c.argument('origin_response_timeout_seconds', type=int,
                   options_list=["--origin-response-timeout-seconds"],
                   help="Send and receive timeout on forwarding request to the origin. "
                        "When timeout is reached, the request fails and returns.")
        c.argument('profile_name', help=profile_name_help, id_part='name')
        c.argument('enabled_state', arg_type=get_enum_type(EnabledState),
                   options_list=["--enabled-state"],
                   help="Whether to enable this endpoint.")
        c.argument('endpoint_name', endpoint_name_type, id_part='child_name_1',
                   help='Name of the endpoint under the profile which is unique globally.')
        c.argument('content_paths', nargs='+',
                   help="The path to the content to be purged. Can describe a file path or a wildcard directory.")
        c.argument('domains', nargs='+', help='List of domains.')

    with self.argument_context('afd endpoint list') as c:
        c.argument('profile_name', id_part=None)

    # AFD Origin Group #
    with self.argument_context('afd origin-group') as c:
        c.argument('origin_group_name', origin_group_name_type, id_part='child_name_1',
                   help='Name of the origin group.')
        c.argument('profile_name', help=profile_name_help, id_part='name')

        # health probe related paramters
        c.argument('probe_request_type', arg_type=get_enum_type(HealthProbeRequestType),
                   help='The type of health probe request that is made.')
        c.argument('probe_protocol', arg_type=get_enum_type(ProbeProtocol),
                   help='Protocol to use for health probe.')
        c.argument('probe_interval_in_seconds', type=int,
                   help='The number of seconds between health probes.')
        c.argument('probe_path',
                   help="The path relative to the origin that is used to determine the health of the origin.")

        # load balancing related parameters
        c.argument('load_balancing_sample_size', type=int,
                   options_list='--sample-size',
                   arg_group="Load Balancing",
                   help="The number of samples to consider for load balancing decisions.")
        c.argument('load_balancing_successful_samples_required', type=int,
                   options_list='--successful-samples-required',
                   arg_group="Load Balancing",
                   help="The number of samples within the sample period that must succeed.")
        c.argument('load_balancing_additional_latency_in_milliseconds', type=int,
                   options_list='--additional-latency-in-milliseconds',
                   arg_group="Load Balancing",
                   help="The additional latency in milliseconds for probes to fall into the lowest latency bucket.")

    with self.argument_context('afd origin-group list') as c:
        c.argument('origin_group_name', id_part=None)
        c.argument('profile_name', id_part=None)

    # AFD Origin #
    with self.argument_context('afd origin') as c:
        c.argument('origin_name', origin_name_type, id_part='child_name_2', help='Name of the origin.')
        c.argument('profile_name', help=profile_name_help, id_part='name')
        c.argument('origin_group_name', origin_group_name_type, id_part='child_name_1',
                   help='Name of the origin group which is unique within the endpoint.')
        c.argument('host_name',
                   help="The address of the origin. Domain names, IPv4 addresses, and IPv6 addresses are supported."
                        "This should be unique across all origins in a origin group.")
        c.argument('origin_host_header',
                   help="The Host header to send for requests to this origin. If you leave this blank, "
                        "the request hostname determines this value. "
                        "Azure CDN origins, such as Web Apps, Blob Storage, and Cloud Services "
                        "require this host header value to match the origin hostname by default.")
        c.argument('http_port', type=int, help="The port used for http requests to the origin.")
        c.argument('https_port', type=int, help="The port used for https requests to the origin.")
        c.argument('enabled_state', arg_type=get_enum_type(EnabledState),
                   help="Whether to enable this origin.")
        c.argument('priority', type=int,
                   help="Priority of origin in given origin group for load balancing. Higher priorities will not be "
                        "used for load balancing if any lower priority origin is healthy. Must be between 1 and 5.")
        c.argument('weight', type=int,
                   help="Weight of the origin in given origin group for load balancing. Must be between 1 and 1000.")
        c.argument('enable_private_link', arg_type=get_three_state_flag(invert=False),
                   help='Indicates whether private link is enanbled on that origin.')
        c.argument('private_link_resource',
                   help="The resource ID of the origin that will be connected to using the private link.")
        c.argument('private_link_location',
                   help="The location of origin that will be connected to using the private link.")
        c.argument(
            'private_link_sub_resource_type',
            help="The sub-resource type of the origin that will be connected to using the private link."
                 'You can use "az network private-link-resource list" to obtain the supported sub-resource types.')
        c.argument('private_link_request_message',
                   help="The message that is shown to the approver of the private link request.")

    with self.argument_context('afd origin list') as c:
        c.argument('profile_name', id_part=None)
        c.argument('origin_group_name', id_part=None)

    # AFD Route #
    with self.argument_context('afd route') as c:
        c.argument('route_name', route_name_type, id_part='child_name_2', help='Name of the route.')
        c.argument('profile_name', help=profile_name_help, id_part='name')
        c.argument('endpoint_name', endpoint_name_type, id_part='child_name_1', help='Name of the endpoint.')
        c.argument('origin_group', help='Name or ID of the origin group to be associated with.')
        c.argument('patterns_to_match', nargs='+', help='The route patterns of the rule.')
        c.argument('origin_path',
                   help='A directory path on the origin that AFD can use to retrieve content from. E.g, "/img/*"')
        c.argument('custom_domains', nargs='*', help='Custom domains referenced by this endpoint.')
        c.argument('supported_protocols', nargs='+',
                   arg_type=get_enum_type(AFDEndpointProtocols),
                   help="List of supported protocols for this route.")
        c.argument('link_to_default_domain',
                   arg_type=get_enum_type(LinkToDefaultDomain),
                   help="Whether this route will be linked to the default endpoint domain.")
        c.argument('forwarding_protocol',
                   arg_type=get_enum_type(ForwardingProtocol),
                   help="Protocol this rule will use when forwarding traffic to backends.")
        c.argument('https_redirect',
                   arg_type=get_enum_type(HttpsRedirect),
                   help='Whether to automatically redirect HTTP traffic to HTTPS traffic.')
        c.argument('rule_sets', nargs='*', help='Collection of ID or name of rule set referenced by the route.')
        c.argument('content_types_to_compress', nargs='+',
                   help='List of content types on which compression applies. The value should be a valid MIME type.')
        c.argument('query_string_caching_behavior',
                   arg_type=get_enum_type(QueryStringCachingBehavior),
                   help="Defines how CDN caches requests that include query strings. "
                        "You can ignore any query strings when caching, "
                        "bypass caching to prevent requests that contain query strings from being cached, "
                        "or cache every request with a unique URL.")
        c.argument(
            'is_compression_enabled',
            arg_type=get_three_state_flag(),
            options_list='--enable-compression',
            help='Indicates whether content compression is enabled on AzureFrontDoor. Default value is false. '
                 'If compression is enabled, content will be served as compressed if user requests for a '
                 "compressed version. Content won't be compressed on AzureFrontDoor when requested content is "
                 'smaller than 1 byte or larger than 1 MB.')

    with self.argument_context('afd route list') as c:
        c.argument('profile_name', id_part=None)
        c.argument('endpoint_name', id_part=None)

    # AFD RuleSets #
    with self.argument_context('afd rule-set') as c:
        c.argument('rule_set_name', rule_set_name_type, id_part='child_name_1', help='Name of the rule set.')
        c.argument('profile_name', help=profile_name_help, id_part='name')

    with self.argument_context('afd rule-set list') as c:
        c.argument('profile_name', id_part=None)

    # AFD Rules #
    with self.argument_context('afd rule') as c:
        c.argument('profile_name', help=profile_name_help, id_part='name')
        c.argument('rule_set_name', id_part='child_name_1', help='Name of the rule set.')
        configure_rule_parameters(c)
        c.argument('rule_name', rule_name_type, id_part='child_name_2', help='Name of the rule.')
        c.argument('match_processing_behavior',
                   arg_type=get_enum_type(MatchProcessingBehavior),
                   help='Indicate whether rules engine should continue to run the remaining rules or stop if matched.'
                        ' Defaults to Continue.')

    with self.argument_context('afd rule list') as c:
        c.argument('profile_name', id_part=None)
        c.argument('rule_set_name', id_part=None)

    with self.argument_context('afd rule condition list') as c:
        c.argument('profile_name', id_part=None)
        c.argument('rule_set_name', id_part=None)
        c.argument('rule_name', id_part=None)

    with self.argument_context('afd rule action list') as c:
        c.argument('profile_name', id_part=None)
        c.argument('rule_set_name', id_part=None)
        c.argument('rule_name', id_part=None)

    # AFD Security Policy #
    with self.argument_context('afd security-policy') as c:
        c.argument('profile_name', help=profile_name_help, id_part='name')
        c.argument('security_policy_name', id_part='child_name_1', help='Name of the security policy.')
        c.argument('waf_policy', help='The ID of Front Door WAF policy.')
        c.argument(
            'domains',
            nargs='+',
            help='The domains to associate with the WAF policy. Could either be the ID of an endpoint'
                 ' (default domain will be used in that case) or ID of a custom domain.')

    with self.argument_context('afd security-policy list') as c:
        c.argument('profile_name', id_part=None)
        c.argument('security_policy_name', id_part=None)

    # AFD Custom Domain #
    with self.argument_context('afd custom-domain') as c:
        c.argument('profile_name', help=profile_name_help, id_part='name')
        c.argument('custom_domain_name', custom_name_arg_type, id_part="child_name_1",
                   help='Name of the custom domain.')
        c.argument('certificate_type', arg_type=get_enum_type(AfdCertificateType),
                   help='Defines the source of the SSL certificate.')
        c.argument('minimum_tls_version', arg_type=get_enum_type(AfdMinimumTlsVersion),
                   help='TLS protocol version that will be used for Https.')
        c.argument('host_name', help='The host name of the domain. Must be a domain name.')
        c.argument('azure_dns_zone', help='ID of the Azure DNS zone.')
        c.argument('secret', help='Name of the azure front door secret.')

    with self.argument_context('afd custom-domain list') as c:
        c.argument('profile_name', id_part=None)
        c.argument('custom_domain_name', custom_name_arg_type, id_part=None, help='Name of the custom domain.')

    # AFD Secret #
    with self.argument_context('afd secret') as c:
        c.argument('profile_name', help=profile_name_help, id_part='name')
        c.argument('secret_name', secret_name_arg_type, id_part="child_name_1", help='Name of the secret.')
        c.argument('use_latest_version', arg_type=get_three_state_flag(),
                   help="Whether to use the latest version for the certificate.")
        c.argument('secret_source', help='ID of the Azure key vault certificate.')
        c.argument('secret_version', help='Version of the certificate to be used.')

    with self.argument_context('afd secret list') as c:
        c.argument('profile_name', id_part=None)
        c.argument('secret_name', id_part=None)

    # AFD Log Analytic #
    with self.argument_context('afd log-analytic') as c:
        c.argument('group_by', nargs='+',
                   arg_type=get_enum_type(["httpStatusCode", "protocol", "cacheStatus", "country", "customDomain"]),
                   help="Aggregate demensions.")
        c.argument('continents', nargs='+', help="ISO 3316-1 alpha-2 continent code.")
        c.argument('country_or_regions', nargs='+', help="ISO 3316-1 alpha-2 region code.")
        c.argument('custom_domains', nargs='+', help="The domains to be included.")
        c.argument('protocols', nargs='+', help="The protocols to be included.")
        configure_log_analytic_common_parameters(c)

    with self.argument_context('afd log-analytic metric') as c:
        c.argument('metrics', nargs='+',
                   arg_type=get_enum_type(["clientRequestCount", "clientRequestTraffic", "clientRequestBandwidth",
                                           "originRequestTraffic", "originRequestBandwidth", "totalLatency"]),
                   help="Metric types to include.")

    with self.argument_context('afd log-analytic ranking') as c:
        c.argument('metrics', nargs='+',
                   arg_type=get_enum_type(["clientRequestCount", "clientRequestTraffic",
                                           "hitCount", "missCount", "userErrorCount", "errorCount"]),
                   help="Metric types to include.")
        c.argument('rankings', nargs='+', help="The dimemsions to be included for ranking.",
                   arg_type=get_enum_type(["url", "referrer", "browser", "userAgent", "countryOrRegion"]))

    with self.argument_context('afd waf-log-analytic') as c:
        c.argument('metrics', nargs='+', arg_type=get_enum_type(["clientRequestCount"]),
                   help="Metric types to be included.")
        c.argument('group_by', nargs='+', arg_type=get_enum_type(["httpStatusCode", "customDomain"]),
                   help="Aggregate demensions.")
        c.argument('actions', nargs='+', help="The WAF actions to be included.",
                   arg_type=get_enum_type(["allow", "block", "log", "redirect"]))
        c.argument('rule_types', nargs='+', help="The WAF rule types to be included.",
                   arg_type=get_enum_type(["managed", "custom", "bot"]))
        c.argument('rankings', nargs='+', help="The dimemsions to be included for ranking.",
                   arg_type=get_enum_type(["action", "ruleGroup", "ruleId", "userAgent",
                                           "clientIp", "url", "country", "ruleType"]))
        configure_log_analytic_common_parameters(c)


def configure_log_analytic_common_parameters(c):
    c.argument('granularity', help="The interval granularity.", arg_type=get_enum_type(["PT5M", "PT1H", "P1D"]))
    c.argument('date_time_begin', help="The start datetime.")
    c.argument('date_time_end', help="The end datetime.")
    c.argument('max_ranking', help="The maximum number of rows to return based on the ranking.")


# pylint: disable=protected-access
def configure_rule_parameters(c):
    c.argument('rule_name', help='Name of the rule.')
    c.argument('order', type=int,
               help='The order in which the rules are applied for the endpoint. Possible values {0,1,2,3,………}. '
               'A rule with a lower order will be applied before one with a higher order. '
               'Rule with order 0 is a special rule. '
               'It does not require any condition and actions listed in it will always be applied.')
    c.argument('match_variable', arg_group="Match Condition", help='Name of the match condition.',
               arg_type=get_enum_type(DeliveryRuleCondition._subtype_map["name"].keys()))
    c.argument('operator', arg_group="Match Condition", help='Operator of the match condition.')
    c.argument('selector', arg_group="Match Condition", help='Selector of the match condition.')
    c.argument('match_values', arg_group="Match Condition", nargs='+',
               help='Match values of the match condition (comma separated).')
    c.argument('transform', arg_group="Match Condition", arg_type=get_enum_type(['Lowercase', 'Uppercase']),
               nargs='+', help='Transform to apply before matching.')
    c.argument('negate_condition', arg_group="Match Condition", arg_type=get_three_state_flag(),
               help='If true, negates the condition')
    actions = ["RequestHeader", "ResponseHeader"]
    actions.extend(DeliveryRuleAction._subtype_map["name"].keys())
    c.argument('action_name', arg_group="Action", help='Name of the action.', arg_type=get_enum_type(actions))
    c.argument('cache_behavior', arg_group="Action",
               arg_type=get_enum_type(['BypassCache', 'Override', 'SetIfMissing']),
               help='Caching behavior for the requests.')
    c.argument('cache_duration', arg_group="Action",
               help='The duration for which the content needs to be cached. \
               Allowed format is [d.]hh:mm:ss.')
    c.argument('header_action', arg_group="Action",
               arg_type=get_enum_type(['Append', 'Overwrite', 'Delete']),
               help='Header action for the requests.')
    c.argument('header_name', arg_group="Action", help='Name of the header to modify.')
    c.argument('header_value', arg_group="Action", help='Value of the header.')
    c.argument('redirect_type', arg_group="Action",
               arg_type=get_enum_type(['Moved', 'Found', 'TemporaryRedirect', 'PermanentRedirect']),
               help='The redirect type the rule will use when redirecting traffic.')
    c.argument('redirect_protocol', arg_group="Action",
               arg_type=get_enum_type(['MatchRequest', 'Http', 'Https']),
               help='Protocol to use for the redirect.')
    c.argument('custom_hostname', arg_group="Action", help='Host to redirect. \
               Leave empty to use the incoming host as the destination host.')
    c.argument('custom_path', arg_group="Action",
               help='The full path to redirect. Path cannot be empty and must start with /. \
               Leave empty to use the incoming path as destination path.')
    c.argument('custom_querystring', arg_group="Action",
               help='The set of query strings to be placed in the redirect URL. \
               leave empty to preserve the incoming query string.')
    c.argument('custom_fragment', arg_group="Action", help='Fragment to add to the redirect URL.')
    c.argument('query_string_behavior', arg_group="Action",
               arg_type=get_enum_type(['Include', 'IncludeAll', 'Exclude', 'ExcludeAll']),
               help='Query string behavior for the requests.')
    c.argument('query_parameters', arg_group="Action",
               help='Query parameters to include or exclude (comma separated).')
    c.argument('source_pattern', arg_group="Action",
               help='A request URI pattern that identifies the type of requests that may be rewritten.')
    c.argument('destination', help='The destination path to be used in the rewrite.')
    c.argument('preserve_unmatched_path', arg_group="Action",
               arg_type=get_three_state_flag(),
               help='If True, the remaining path after the source \
               pattern will be appended to the new destination path.')
    c.argument('index', type=int, help='The index of the condition/action')
    c.argument('origin_group', arg_group="Action",
               help='Name or ID of the OriginGroup that would override the default OriginGroup')
