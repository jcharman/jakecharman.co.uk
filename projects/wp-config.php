<?php
/**
 * The base configuration for WordPress
 *
 * The wp-config.php creation script uses this file during the installation.
 * You don't have to use the web site, you can copy this file to "wp-config.php"
 * and fill in the values.
 *
 * This file contains the following configurations:
 *
 * * Database settings
 * * Secret keys
 * * Database table prefix
 * * ABSPATH
 *
 * @link https://wordpress.org/support/article/editing-wp-config-php/
 *
 * @package WordPress
 */

// ** Database settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', 'projects' );

/** Database username */
define( 'DB_USER', 'projects' );

/** Database password */
define( 'DB_PASSWORD', 'eEzK7AAumKtHxL' );

/** Database hostname */
define( 'DB_HOST', 'localhost' );

/** Database charset to use in creating database tables. */
define( 'DB_CHARSET', 'utf8mb4' );

/** The database collate type. Don't change this if in doubt. */
define( 'DB_COLLATE', '' );

/**#@+
 * Authentication unique keys and salts.
 *
 * Change these to different unique phrases! You can generate these using
 * the {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}.
 *
 * You can change these at any point in time to invalidate all existing cookies.
 * This will force all users to have to log in again.
 *
 * @since 2.6.0
 */
define( 'AUTH_KEY',         '4!:P39xw 6~V]M5raK5NmB~5Tr%.2gj#m~%Hkr=*D~<^/?=.;([|4Ut(iD,!uJ=h' );
define( 'SECURE_AUTH_KEY',  '<5uMDu8V]8*_uY_i1heh9dv[J 60|`[aG~K=.d< L.^43K{_CdO{9`~FbPk*HI;f' );
define( 'LOGGED_IN_KEY',    '`{I<?N]ct;S<}hWXF5L6L:R6t}2{K<7-+[NY$?pnH.9_n4YR*3v>h1!EYDuQjK1F' );
define( 'NONCE_KEY',        'z@=mPy @@12GJmxd#rKFP,JY,Nng^ LSH.W=uf(b,n!BGnijIvy:ufQ10}zt-!?r' );
define( 'AUTH_SALT',        'Mu4P;tp-L|r[;((c:8JW+CA*796g*wX1Z7>&A<9w+|e6s[CU_JAD21q<,Qfq3xKv' );
define( 'SECURE_AUTH_SALT', 'Wuq7iY~G-L<.uN/:+:UOE.S8@M-qVhPyp]ouvUsXYFhGTfOh>z:p:acm|yMLOMU-' );
define( 'LOGGED_IN_SALT',   'xYl~Kz)]= E&bW~p5*WA|i%hsG>>>pR?LgcGYqrI8.;ELW=>#(~4b$]2#Cg=MMO!' );
define( 'NONCE_SALT',       'f,M;&ZFBI@_xDI<#,r?U8&X+f[h*7VS=[AeB`IsZeF*G]47>iA~p7I(AkGDl11Kr' );

/**#@-*/

/**
 * WordPress database table prefix.
 *
 * You can have multiple installations in one database if you give each
 * a unique prefix. Only numbers, letters, and underscores please!
 */
$table_prefix = 'wp_';

/**
 * For developers: WordPress debugging mode.
 *
 * Change this to true to enable the display of notices during development.
 * It is strongly recommended that plugin and theme developers use WP_DEBUG
 * in their development environments.
 *
 * For information on other constants that can be used for debugging,
 * visit the documentation.
 *
 * @link https://wordpress.org/support/article/debugging-in-wordpress/
 */
define( 'WP_DEBUG', false );

/* Add any custom values between this line and the "stop editing" line. */



/* That's all, stop editing! Happy publishing. */

/** Absolute path to the WordPress directory. */
if ( ! defined( 'ABSPATH' ) ) {
	define( 'ABSPATH', __DIR__ . '/' );
}

/** Sets up WordPress vars and included files. */
require_once ABSPATH . 'wp-settings.php';
