import React from 'react';
import { connect } from 'react-redux';
import { push } from 'react-router-redux';
import classNames from 'classnames';
import PropTypes from 'prop-types';
import Facebook from './components/Facebook';

import { authLogoutAndRedirect } from './actions/auth';
import './styles/main.scss';

class App extends React.Component {
    static propTypes = {
        isAuthenticated: PropTypes.bool.isRequired,
        children: PropTypes.shape().isRequired,
        dispatch: PropTypes.func.isRequired,
        location: PropTypes.shape({
            pathname: PropTypes.string
        })
    };

    static defaultProps = {
        location: undefined
    };

    logout = () => {
        this.props.dispatch(authLogoutAndRedirect());
    };

    goToIndex = () => {
        this.props.dispatch(push('/'));
    };

    goToLogin = () => {
        this.props.dispatch(push('/login'));
    };

    goToProtected = () => {
        this.props.dispatch(push('/protected'));
    };

    render() {
        const homeClass = classNames({
            active: this.props.location && this.props.location.pathname === '/'
        });
        const protectedClass = classNames({
            active: this.props.location && this.props.location.pathname === '/protected'
        });
        const loginClass = classNames({
            active: this.props.location && this.props.location.pathname === '/login'
        });

        return (
            <div className="app">
                <nav className="navbar navbar-default">
                    <div className="container-fluid">
                        <div className="navbar-header">
                            <button type="button"
                                className="navbar-toggle collapsed"
                                data-toggle="collapse"
                                data-target="#top-navbar"
                                aria-expanded="false"
                            >
                                <span className="sr-only">Toggle navigation</span>
                                <span className="icon-bar" />
                                <span className="icon-bar" />
                                <span className="icon-bar" />
                            </button>
                            <a className="navbar-brand" onClick={this.goToIndex}>
                                Trident
                            </a>
                        </div>
                        <div className="collapse navbar-collapse" id="top-navbar">
                            {this.props.isAuthenticated ?
                                <ul className="nav navbar-nav navbar-right">
                                    <li className={homeClass}>
                                        <a className="js-go-to-index-button" onClick={this.goToIndex}>
                                            <i className="fa fa-home" /> Home
                                        </a>
                                    </li>
                                    <li className={protectedClass}>
                                        <a className="js-go-to-protected-button" onClick={this.goToProtected}>
                                            <i className="fa fa-lock" /> My Profile
                                        </a>
                                    </li>
                                    <li>
                                        <a className="js-logout-button" onClick={this.logout}>
                                            Logout
                                        </a>
                                    </li>
                                </ul>
                                :
                                <ul className="nav navbar-nav navbar-right">
                                    <li className={homeClass}>
                                        <a className="js-go-to-index-button" onClick={this.goToIndex}>
                                            <i className="fa fa-home" /> Home
                                        </a>
                                    </li>
                                    <li className={loginClass}>
                                        <a className="js-login-button" onClick={this.goToLogin}>
                                            <i className="fa fa-home" /> Login
                                        </a>
                                    </li>
                                    <li>
                                        <i className="fa fa-home" />
                                        <Facebook/>
                                    </li>
                                </ul>
                            }
                        </div>
                    </div>
                </nav>

                <div>
                    {this.props.children}
                </div>
            </div>
        );
    }
}

const facebookResponse = (response) => {
    const tokenBlob = new Blob([JSON.stringify({access_token: response.accessToken}, null, 2)], {type : 'application/json'});
    const options = {
        method: 'POST',
        body: tokenBlob,
        mode: 'cors',
        cache: 'default'
    };
    fetch('http://localhost:4000/login/facebook', options).then(r => {
        const token = r.headers.get('x-auth-token');
        r.json().then(user => {
            if (token) {
                this.setState({isAuthenticated: true, user, token})
            }
        });
    })
};

const responseFacebook = (response) => {
    console.log(response);
  }

const mapStateToProps = (state, ownProps) => {
    return {
        isAuthenticated: state.auth.isAuthenticated,
        location: state.routing.location
    };
};

export default connect(mapStateToProps)(App);
export { App as AppNotConnected };
